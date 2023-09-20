import argparse
import os
from time import sleep
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def parse_book_page(response):

    txt_url = 'https://tululu.org/txt.php'

    soup = BeautifulSoup(response.text, 'lxml')

    header_text = soup.select_one('h1').text
    book_name, book_autor = header_text.split('::')

    book_name = book_name.strip()
    book_autor = book_autor.strip()

    genres_tags = soup.select('span.d_book a')
    genres = [genres_tag.text for genres_tag in genres_tags]

    comment_tags = soup.select('.texts .black')
    comments = [comment_tag.text for comment_tag in comment_tags]

    image_filename = soup.select_one('div.bookimage img')['src'].split('/')[-1]
    book_image_url = urljoin(response.url, soup.select_one('.bookimage img')['src'])
    book_text_url = urljoin(txt_url, soup.select('table.d_book a')[-3]['href'])
    txt_filename = f'{book_name}.txt'

    book_description = {
        'book_name': book_name,
        'author': book_autor,
        'image_url': book_image_url,
        'image_filename': image_filename,
        'text_url': book_text_url,
        'txt_filename': txt_filename,
        'genres': genres,
        'comments': comments,
    }
    return book_description


def download_txt(response, filename, folder='books'):

    Path(folder).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(file_path, 'wb') as file:
        file.write(response.content)

    return file_path


def download_image(image_url, folder='images'):

    parser_url = urlparse(image_url)
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()
    check_for_redirect(response)
    file_path = os.path.join(folder, parser_url.path.split('/')[-1])
    with open(file_path, 'wb') as file:
        file.write(response.content)


def main():

    parser = argparse.ArgumentParser(description='Парсер книг')
    parser.add_argument('--start_id', help='Введите стартовый id', default=1, type=int)
    parser.add_argument('--end_id', help='Введите конечный id', default=10, type=int)
    arguments = parser.parse_args()
    start_id = arguments.start_id
    end_id = arguments.end_id

    for book_id in range(start_id, end_id + 1):
        try:
            response = requests.get(f'https://tululu.org/b{book_id}/')
            response.raise_for_status()
            check_for_redirect(response)
            book = parse_book_page(response)

            response = requests.get('https://tululu.org/txt.php', params={'id': book_id})
            response.raise_for_status()
            check_for_redirect(response)

            download_txt(response, f'{book_id}. {book["book_name"]}')
            download_image(book['image_url'])

        except requests.exceptions.HTTPError:
            print(f'Книга не найдена: {book_id}')
        except requests.exceptions.ConnectionError:
            print('Ожидаем соединение 60 секунд')
            sleep(60)


if __name__ == '__main__':
    main()

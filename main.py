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


def parse_book_page(response, book_id):

    soup = BeautifulSoup(response.text, 'lxml')

    header_text = soup.select_one('h1').text
    book_name, book_autor = header_text.split('::')
    book_name = book_name.strip()
    book_autor = book_autor.strip()
    comment_tags = soup.select('.texts .black')
    comments = [comment_tag.text for comment_tag in comment_tags]
    genres_tags = soup.select('span.d_book a')
    genres = [genres_tag.text for genres_tag in genres_tags]
    image_url = urljoin(response.url, soup.select_one('.bookimage img')['src'])

    book = {
            'book_id': book_id,
            'book_name': book_name,
            'author': book_autor,
            'comments': comments,
            'image_url': image_url,
            'genres': genres
            }
    return book


def download_txt(url, book_id, filename, folder='books'):

    Path(folder).mkdir(parents=True, exist_ok=True)

    response = requests.get(url, params={'id': book_id})
    response.raise_for_status()
    file_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(file_path, 'wb') as file:
        file.write(response.content)

    return file_path


def download_image(image_url, folder='images'):

    parser_url = urlparse(image_url)
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()
    file_path = os.path.join(folder, parser_url.path.split('/')[-1])
    with open(file_path, 'wb') as file:
        file.write(response.content)


def main():

    parser = argparse.ArgumentParser(description='Парсер книг')
    parser.add_argument('--start_id', help='Введите стартовый id', default=10, type=int)
    parser.add_argument('--end_id', help='Введите конечный id', default=100, type=int)
    arguments = parser.parse_args()
    start_id = arguments.start_id
    end_id = arguments.end_id

    for book_id in range(start_id, end_id + 1):
        try:
            response = requests.get(f'https://tululu.org/b{book_id}/')
            response.raise_for_status()
            check_for_redirect(response)
            book = parse_book_page(response, book_id)
            download_txt('https://tululu.org/txt.php', book_id, f'{book_id}. {book["book_name"]}')
            download_image(book['image_url'])

        except requests.exceptions.HTTPError:
            print(f'Книга не найдена: {book_id}')
        except requests.exceptions.ConnectionError:
            print('Ожидаем соединение 60 секунд')
            sleep(60)


if __name__ == '__main__':
    main()

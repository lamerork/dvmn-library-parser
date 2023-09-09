import json
from time import sleep
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from tqdm import tqdm

from main import download_txt, download_image, check_for_redirect


def parse_book_url(response, page_url):

    soup = BeautifulSoup(response.text, 'lxml')

    books_ids = soup.find_all('table', class_='d_book')
    book_urls = [urljoin(page_url, book_id.find('a')['href']) for book_id in books_ids]
    return book_urls


def parse_book_page(response, page_url):

    soup = BeautifulSoup(response.text, 'lxml')

    book_name, author = soup.find('h1').text.split('::')
    genres = soup.find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in genres]
    comment_tags = soup.find_all(class_='texts')
    comments = [comment.find('span', class_='black').text for comment in comment_tags]
    book_image = soup.find('div', class_='bookimage').find('img')['src']
    book_image_url = urljoin(page_url, soup.find('div', class_='bookimage').find('img')['src'])
    image_filename = book_image.split('/')[2]
    book_text_url = urljoin(page_url, soup.find('table', class_='d_book').find_all('a')[-3]['href'])

    book_description = {
        'book_name': book_name.strip(),
        'author': author.strip(),
        'image_url': book_image_url,
        'image_filename': image_filename,
        'text_url': book_text_url,
        'genres': book_genres,
        'comments': comments,
    }
    return book_description


def main():

    book_urls = []
    book_descriptions = []

    #parser = argparse.ArgumentParser(description='Парсер книг')
    #parser.add_argument('--start_id', help='Введите стартовый id', default=1, type=int)
    #parser.add_argument('--end_id', help='Введите конечный id', default=10, type=int)
    #arguments = parser.parse_args()
    #start_id = arguments.start_id
    #end_id = arguments.end_id

    for page in tqdm(range(1, 11), bar_format="{l_bar}{bar:50}{r_bar}", desc ="Получение ссылок"):
        category_page_url = f'https://tululu.org/l55/{page}'
        category_page_response = requests.get(category_page_url)
        category_page_response.raise_for_status()
        book_urls.extend(parse_book_url(category_page_response, category_page_url))

    for book_url in tqdm(book_urls, bar_format="{l_bar}{bar:50}{r_bar}", desc ="Скачивание книг"):

        try:
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            book_description = parse_book_page(response, book_url)
            book_descriptions.append(book_description)

            response = requests.get(book_description['text_url'])
            response.raise_for_status()
            check_for_redirect(response)

            download_txt(response, book_description['book_name'])
            download_image(book_description['image_url'])

        except requests.exceptions.HTTPError:
            print(f'Книга не найдена: {book_description["book_name"]}')
        except requests.exceptions.ConnectionError:
            print('Ожидаем соединение 60 секунд')
            sleep(60)

    with open('Catalog.json', 'w', encoding='utf8') as json_file:
        json.dump(book_descriptions, json_file,
                  ensure_ascii=False,
                  sort_keys=True,
                  indent=4)


if __name__ == '__main__':

    main()

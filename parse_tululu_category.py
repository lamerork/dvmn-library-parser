import argparse
import json
from time import sleep
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from tqdm import tqdm
from colorama import Fore
import logging
from parse_tululu import download_txt, download_image, check_for_redirect, parse_book_page


def parse_catalog_page(response, page_url):

    soup = BeautifulSoup(response.text, 'lxml')

    all_books_page = soup.select('.d_book div.bookimage a')
    book_urls = [urljoin(page_url, book['href']) for book in all_books_page]

    return book_urls


def main():

    logging.basicConfig(level=logging.INFO)

    book_urls = []
    book_descriptions = []

    parser = argparse.ArgumentParser(description='Скачивание и сохранение книг по категориям')
    parser.add_argument('--start_page', help='Номер начальной страницы', default=1, type=int)
    parser.add_argument('--end_page', help='Номер финальной страницы', default=10, type=int)
    parser.add_argument('--skip_imgs', help='Не скачивать картинки', action='store_true')
    parser.add_argument('--skip_txt', help='Не скачивать книги', action='store_true')
    parser.add_argument('--dest_folder', help='Не скачивать книги', default='books', type=str)
    arguments = parser.parse_args()

    pages = range(arguments.start_page, arguments.end_page + 1)

    for page in tqdm(pages,
                    bar_format='%s{l_bar}%s{bar:50}%s{r_bar}' % (Fore.YELLOW, Fore.BLUE, Fore.YELLOW), 
                    desc ='Получение ссылок'):

        category_page_url = f'https://tululu.org/l55/{page}'

        try:
            category_page_response = requests.get(category_page_url)
            category_page_response.raise_for_status()
            check_for_redirect(category_page_response)
            book_urls.extend(parse_catalog_page(category_page_response, category_page_url))

        except requests.exceptions.HTTPError:
            logging.info(f'Не удалось загрузить страницу: {page}')

        except requests.exceptions.ConnectionError:
            logging.info('Ожидаем соединение 60 секунд')
            sleep(60)

    for book_url in tqdm(book_urls, 
                        bar_format='%s{l_bar}%s{bar:50}%s{r_bar}' % (Fore.YELLOW, Fore.GREEN, Fore.YELLOW), 
                        desc ='Скачивание книг'):
        try:
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            book_description = parse_book_page(response)
            book_descriptions.append(book_description)

            if not arguments.skip_txt:
                response = requests.get(book_description['text_url'])
                response.raise_for_status()
                check_for_redirect(response)
                download_txt(response, book_description['book_name'], f'{arguments.dest_folder}/txt')

            if not arguments.skip_imgs:
                download_image(book_description['image_url'], f'{arguments.dest_folder}/img')

        except requests.exceptions.HTTPError:
            logging.info(f'Не удалось скачать книгу: {book_description["book_name"]}')

        except requests.exceptions.ConnectionError:
            logging.info('Ожидаем соединение 60 секунд')
            sleep(60)

    with open(f'{arguments.dest_folder}/Catalog.json', 'w', encoding='utf8') as json_file:
        json.dump(book_descriptions, json_file,
                  ensure_ascii=False,
                  sort_keys=True,
                  indent=4)


if __name__ == '__main__':

    main()

import argparse
import json
from time import sleep
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from tqdm import tqdm
from colorama import Fore
from main import download_txt, download_image, check_for_redirect


def parse_book_url(response, page_url):

    soup = BeautifulSoup(response.text, 'lxml')

    books_ids = soup.select('.d_book div.bookimage a')
    book_urls = [urljoin(page_url, book_id['href']) for book_id in books_ids]

    return book_urls


def parse_book_page(response, page_url):

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
    book_text_url = urljoin(page_url, soup.select_one('table.d_book a')['href'])

    book_description = {
        'book_name': book_name,
        'author': book_autor,
        'image_url': book_image_url,
        'image_filename': image_filename,
        'text_url': book_text_url,
        'genres': genres,
        'comments': comments,
    }
    return book_description


def main():

    book_urls = []
    book_descriptions = []

    parser = argparse.ArgumentParser(description='Скачивание и сохранение книг по категориям')
    parser.add_argument('--start_page', help='Номер начальной страницы', default=1, type=int)
    parser.add_argument('--end_page', help='Номер финальной страницы', default=2, type=int)
    parser.add_argument('--skip_imgs', help='Не скачивать картинки', default=False, type=bool)
    parser.add_argument('--skip_txt', help='Не скачивать книги', default=False, type=bool)
    parser.add_argument('--dest_folder', help='Не скачивать книги', default='books', type=str)
    arguments = parser.parse_args()
 

    for page in tqdm(range(arguments.start_page, arguments.end_page + 1), 
                     bar_format='%s{l_bar}%s{bar:50}%s{r_bar}' % (Fore.YELLOW, Fore.BLUE, Fore.YELLOW), 
                     desc ='Получение ссылок'):
        
        category_page_url = f'https://tululu.org/l55/{page}'
        category_page_response = requests.get(category_page_url)
        category_page_response.raise_for_status()
        book_urls.extend(parse_book_url(category_page_response, category_page_url))

    for book_url in tqdm(book_urls, 
                         bar_format='%s{l_bar}%s{bar:50}%s{r_bar}' % (Fore.YELLOW, Fore.GREEN, Fore.YELLOW), 
                         desc ='Скачивание книг'):

        try:
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            book_description = parse_book_page(response, book_url)
            book_descriptions.append(book_description)

            response = requests.get(book_description['text_url'])
            response.raise_for_status()
            check_for_redirect(response)
            if not arguments.skip_txt:
                download_txt(response, book_description['book_name'], f'{arguments.dest_folder}/txt')
            if not arguments.skip_imgs:
                download_image(book_description['image_url'], f'{arguments.dest_folder}/img')

        except requests.exceptions.HTTPError:
            pass
#            print(f'Книга не найдена: {book_description["book_name"]}')
        except requests.exceptions.ConnectionError:
#            print('Ожидаем соединение 60 секунд')
            sleep(60)

    with open(f'{arguments.dest_folder}/Catalog.json', 'w', encoding='utf8') as json_file:
        json.dump(book_descriptions, json_file,
                  ensure_ascii=False,
                  sort_keys=True,
                  indent=4)


if __name__ == '__main__':

    main()

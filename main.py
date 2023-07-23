import os
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def parse_book(response):

    soup = BeautifulSoup(response.text, 'lxml')
    book_name_parsed = soup.find('h1')
    return book_name_parsed.text.split(' \xa0 :: \xa0 ')[0]



def get_books(folder):

    for book_id in range(11):
        try:
            response = requests.get(f'https://tululu.org/b{book_id}/')
            response.raise_for_status()
            check_for_redirect(response)
            book_name = parse_book(response)
            print(book_id, book_name)
            download_txt(f'https://tululu.org/txt.php?id={book_id}', f'{book_id}. {parse_book(response)}')
            
        except requests.exceptions.HTTPError:
            pass


def download_txt(url, filename, folder='books'):

    Path(folder).mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
        with open(file_path, 'wb') as file:
            file.write(response.content)
    except requests.exceptions.HTTPError:
        return

    return file_path


def main():
  
    get_books('folder')


if __name__ == '__main__':
    main()

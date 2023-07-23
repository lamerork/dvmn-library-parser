import os
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def parse_book(response):

    soup = BeautifulSoup(response.text, 'lxml')

    book_name_parsed = soup.select_one('h1')
    comments = soup.select('.texts .black')
    genres = soup.select('span.d_book a')
    for genre in genres:
        print(genre.text)
 #   for comment in comments:    
 #       print(comment.text)
    return book_name_parsed.text.split(' \xa0 :: \xa0 ')[0] , urljoin('https://tululu.org', soup.select_one('.bookimage img')['src'])
  


def get_books():

    for book_id in range(11):
        try:
            response = requests.get(f'https://tululu.org/b{book_id}/')
            response.raise_for_status()
            check_for_redirect(response)
            book_name, image_url = parse_book(response)
            print(book_id, book_name)
 #           download_txt(f'https://tululu.org/txt.php?id={book_id}', f'{book_id}. {parse_book(response)}')
 #           download_image(image_url)
            
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

def download_image(image_url, folder='images'):


    parser_url = urlparse(image_url)
    print(parser_url.path)
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()
    print(parser_url.path.split('/')[-1])
    file_path = os.path.join(folder, parser_url.path.split('/')[-1])
    with open(file_path, 'wb') as file:
        file.write(response.content)


def main():
  
    get_books()


if __name__ == '__main__':
    main()

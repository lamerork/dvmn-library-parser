import requests
from pathlib import Path

def get_books():

    for book_id in range(10):
        url = f'https://tululu.org/txt.php?id={book_id}'

        response = requests.get(url)
        response.raise_for_status()
 
        filename = f'book/{book_id}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)


def main():

    Path('book').mkdir(parents=True, exist_ok=True)

    get_books()


if __name__ == '__main__':
    main()

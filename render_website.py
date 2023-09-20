import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_book_descriptions():

    path_file = os.path.join('books', 'Catalog.json')

    with open(path_file, "r", encoding='utf-8') as books:
        books_pages = books.read()
    books_descriptions = json.loads(books_pages)

    return books_descriptions


def rebuild_page(folder='pages'):
    env = Environment(
        loader=FileSystemLoader(''),
        autoescape=select_autoescape(['html']))

    Path(folder).mkdir(parents=True, exist_ok=True)

    template = env.get_template('template.html')
    book_descriptions = get_book_descriptions()
    group_books = list(chunked(book_descriptions, 2))
    rendered_page = template.render(group_books=group_books)

    file_path = os.path.join(folder, 'index.html')

    with open(file_path, 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():

    rebuild_page()

    server = Server()
    server.watch('template.html', rebuild_page)
    server.serve(root='pages')


if __name__ == '__main__':

    main()

import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_book_descriptions():

    path_file = os.path.join('books', 'Catalog.json')

    with open(path_file, "r", encoding='utf-8') as books:
        books_pages = books.read()
    books_descriptions = json.loads(books_pages)

    return books_descriptions


def rebuild_page():
    env = Environment(
        loader=FileSystemLoader(''),
        autoescape=select_autoescape(['html']))

    template = env.get_template('template.html')
    book_descriptions = get_book_descriptions()
    group_books = list(chunked(book_descriptions, 2))
    page_group_books = list(chunked(group_books, 10))

    total_page = len(page_group_books)

    for number_page, page_books in enumerate(page_group_books, 1):

        rendered_page = template.render(group_books=page_books, number_page=number_page, total_page=total_page)
        path_filename = os.path.join('pages', f'index{number_page}.html')
        with open(path_filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():

    rebuild_page()

    server = Server()
    server.watch('template.html', rebuild_page)
    server.serve(root='', default_filename='pages/index1.html')


if __name__ == '__main__':

    main()

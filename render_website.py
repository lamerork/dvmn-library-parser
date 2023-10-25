import argparse
import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


PAGE_COLUMNS = 2
PAGE_LINES = 10


def get_book_descriptions(filename):

    with open(filename, 'r', encoding='utf-8') as file:
        books_descriptions = json.load(file)

    return books_descriptions


def rebuild_page(path_folder, path_filename):

    env = Environment(
        loader=FileSystemLoader(''),
        autoescape=select_autoescape(['html']))

    template = env.get_template('template.html')
    book_descriptions = get_book_descriptions(path_filename)
    group_books = list(chunked(book_descriptions, PAGE_COLUMNS))
    page_group_books = list(chunked(group_books, PAGE_LINES))

    end_page = len(page_group_books)

    for number_page, page_books in enumerate(page_group_books, 1):

        rendered_page = template.render(group_books=page_books, number_page=number_page, total_page=end_page)
        path_filename = os.path.join(path_folder, f'index{number_page}.html')
        with open(path_filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():

    parser = argparse.ArgumentParser(description='Рендеринг сохраненных книг')
    parser.add_argument('--path_filename', help='Путь к файлу каталогу', default='media/Catalog.json', type=str)
    parser.add_argument('--path_folder', help='Каталог для хранения файлов', default='pages', type=str)
    arguments = parser.parse_args()

    Path(arguments.path_folder).mkdir(parents=True, exist_ok=True)

    path_folder = arguments.path_folder
    path_filename = arguments.path_filename

    rebuild_page(path_folder, path_filename)

    server = Server()
    server.watch('template.html', lambda: rebuild_page(path_folder, path_filename))
    server.serve(root='', default_filename=f'{arguments.path_folder}/index1.html')


if __name__ == '__main__':

    main()

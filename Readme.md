# Парсер книг с сайта tululu.org
Проект позволяет скачивать книги и их обложки с сайта [tululu.org](https://tululu.org/) по их id.
При скачивании книг можно указывать диапазон парсинга. Обложки скачиваются в отдельную папку.
## Как установить
Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
>>>pip install -r requirements.txt
```
## Как использовать

### Скачивание книг по id
Для скачивания книг по id используется следующая команда:
```python
>>>python parse_tululu.py
```
При запуске можно указать диапазон парсинга для id книг (по умолчанию идёт от 1 до 10), для этого 
указываются значения аргументов `--start_id` и `--end_id`:
```python
>>>python parse_tululu.py --start_id 10 --end_id 12
```
Пример вывода
```
Бизнес путь: Amazon.com
['Деловая литература']
Бизнес путь: Yahoo! Секреты самой популярной в мире интернет-компании
['Деловая литература', 'Прочая компьютерная литература']
Бизнес со скоростью мысли
['Деловая литература']
```

### Скачивание книг по категориям
Для скачивания книг по категориям используется следующая команда:
```python
>>>python parse_tululu_category.py
```
Дополнительные параметры:

`--start_page` - Стартовая страница парсинга
`--end_page` - Финальная страница парсинга
`--skip_txt` - Не скачивать текст книги
`--skip_imgs` -  Не скачивать обложку книги
`--dest_folder` - Можно задать свой путь к папке

Пример использования:
```bash
>>>python parse_tululu_category.py --start_page 1 --end_page 2 

Получение ссылок: 100%|██████████████████████████████████████████████████| 2/2 [00:00<00:00,  3.87it/s]
Скачивание книг: 100%|██████████████████████████████████████████████████| 50/50 [00:32<00:00,  1.53it/s]
```

### Создаем страницы 

Для создания страниц используется следующая команда:
```python
>>>python render_website.py
```
Дополнительные параметры:

`--path_filename` - Путь к файлу json
`--path_folder` - Задать путь к папке для сохранения файлов

Пример использования:
```bash
>>>python parse_render_website.py --path_filename catalog.json --path_folder pages

После запуска сервера, открыть библиотеку можно будет по адресу http://127.0.0.1:5500/




""" db.exports

    Use this file to export data from the database to a local file.
"""

import os, csv

from db.models import Book, BookVolume, BookChapter, create_new_session
from scraper.utils import OUTPUT_DIR

EXPORT_DIR = f"{OUTPUT_DIR}/exports"
os.makedirs(f"{EXPORT_DIR}", exist_ok=True)

def export_book_cat_csv():
    session = create_new_session()
    books = session.query(Book).all()
    filename = 'book_cat_urls.csv'

    if books is not None:
        headers = ['book_id', 'title', 'cat_id', 'url']
        create_csv_file(filename, headers)
        for book in books:
            rows = book.id, book.title, book.category_id, book.import_data["web_url"]
            save_book_data(filename, rows)

    session.close()

# Create CSV file to save data
def create_csv_file(filename, header_list):
  file = open(f"{EXPORT_DIR}/{filename}", 'w', newline='')
  writer = csv.writer(file)
  headers = header_list
  writer.writerow(headers)

# Save row of book data to CSV
def save_book_data(filename, row_list):
  file = open(f"{EXPORT_DIR}/{filename}", 'a', newline='', encoding='utf-8')
  writer = csv.writer(file)
  rows = (row_list)
  writer.writerow(rows)
  file.close()
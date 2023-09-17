from scraper.scrapers import scrape_book, bulk_scrape_books
from db.models import Book, BookVolume, BookChapter
from db.cleaners import (
    process_body_center_tags,
    bulk_process_body_center_tags,
    update_book_sequence,
    bulk_update_book_sequences,
    clean_trailing_periods_from_title,
    clip_book_chapter_titles,
    bulk_update_book_import_data_web_urls,
)

"""
    Example 1: Scrape a single book
    ===> scrape_book(38)

    Example 2: Bulk Scrape a list of books
    ===> bulk_scrape_batch = [1416, 1430, 1431, 1432, 1434, 1435, 1436, 1439, 1441, 1443]
    ===> bulk_scrape_books(bulk_scrape_batch)

    Example 3: Cleaning chapter body <center> tags
    ===> [one] process_body_center_tags(chapter_id)
    ===> [all] bulk_process_body_center_tags()

    Example 4: Update book_sequence for book chapters
    ===> [one] update_book_sequence(book_id)
    ===> [all] bulk_update_book_sequences()

    Example 5: Clean trailing periods from titles in a Class
    ===> clean_trailing_periods_from_title(BookChapter)

    Example 6: Clip book chapter titles for a given book
    ===> clip_book_chapter_titles(book_id)

    Example 7: Update CDN urls in book.import_data for all books
    ===> bulk_update_book_import_data_web_urls()
"""
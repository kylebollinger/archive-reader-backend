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
    bulk_update_book_vol_import_data_web_urls,
    bulk_update_book_chap_import_data_web_urls,
    bulk_update_chapter_body_asset_urls,
    bulk_update_book_state,
)
from db.exports import export_book_cat_csv

"""
    DB Cleaner Examples


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

    Example 8: Update CDN urls in volume.import_data for all volumes
    ===> bulk_update_book_vol_import_data_web_urls()

    Example 9: Update CDN urls in chapter.import_data for all chapters
    ===> bulk_update_book_chap_import_data_web_urls()

    Example 10: Update CDN urls in chapter.body for all chapters
    ===> bulk_update_chapter_body_asset_urls()

    Example 11: Update book.state ('incomplete' |'completed') for all books
    ===> bulk_update_book_state()
"""


"""
    DB Export Examples


    Example 11: Export book category with book homepage url to CSV
    ===> export_book_cat_csv()
"""
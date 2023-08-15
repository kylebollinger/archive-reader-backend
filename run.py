from scraper.scrapers import scrape_book, bulk_scrape_books
from db.cleaners import eliminate_body_headers

"""
    Example 1: Scrape a single book
    ===> scrape_book(38)

    Example 2: Bulk Scrape a list of books
    ===> bulk_scrape_batch = [1416, 1430, 1431, 1432, 1434, 1435, 1436, 1439, 1441, 1443]
    ===> bulk_scrape_books(bulk_scrape_batch)
"""

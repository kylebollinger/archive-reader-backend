""" db.cleaners

    Use this file to perform direct db operations to clean data post scraping
"""
import os, sys, re
from bs4 import BeautifulSoup
print(f"path:\n{sys.path}")

from .models import Book, BookVolume, BookChapter, create_new_session
from scraper.processors import clean_center_tags


def eliminate_body_headers(chapter_id):
    session = create_new_session()
    chapter = session.query(BookChapter).filter_by(id=chapter_id).first()

    if chapter is not None:
        cleaned_body = clean_center_tags(chapter.body)
        chapter.body = cleaned_body
        session.add(chapter)
        session.commit()
    else:
        print(f"[ERROR] ===> Chapter with id {chapter_id} not found")

    session.close()

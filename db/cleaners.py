""" db.cleaners

    Use this file to perform direct db operations to clean data post scraping
"""
import os, sys, re
from bs4 import BeautifulSoup
print(f"path:\n{sys.path}")

from db.models import Book, BookVolume, BookChapter, create_new_session
from scraper.processors import clean_center_tags


""" Clears the chapter.body of all headers and footers """
def process_body_center_tags(chapter_id):
    session = create_new_session()
    chapter = session.query(BookChapter).filter_by(id=chapter_id).first()

    if chapter is not None:
        cleaned_body = clean_center_tags(chapter.body)
        chapter.body = cleaned_body
        session.add(chapter)
        session.commit()
        print(f"[SUCCESS] ===> [{chapter.id}] Chapter Cleaned")
    else:
        print(f"[ERROR] ===> [{chapter.id}] Chapter not found")

    session.close()


def bulk_process_body_center_tags():
    session = create_new_session()
    chapters = session.query(BookChapter).all()

    if chapters is not None:
        for chapter in chapters:
            process_body_center_tags(chapter.id)

    session.close()


""" Loop through and update book sequence for a given book """
def update_book_sequence(book_id):
    unprocessed = []
    session = create_new_session()
    book = session.query(Book).filter_by(id=book_id).first()

    if book is not None:
        book_sequence = 0
        volumes = session.query(BookVolume).filter_by(book_id=book_id).order_by(BookVolume.sequence).all()

        if volumes is not None:
            for volume in volumes:
                chapters = session.query(BookChapter).filter_by(volume_id=volume.id).order_by(BookChapter.sequence).all()

                if chapters is not None:
                    for chapter in chapters:
                        book_sequence += 1
                        chapter.book_sequence = book_sequence
                        session.add(chapter)
                        session.commit()
                    print(f"[SUCCESS] ===> [{book.id}]-[{volume.id}] Chapters Updated")
                else:
                    print(f"[ERROR] ===> [{volume.id}] Volume has no chapters")
                    unprocessed.append(volume.id)

def bulk_update_book_sequences():
    session = create_new_session()
    books = session.query(Book).all()

    if books is not None:
        for book in books:
            update_book_sequence(book.id)

    session.close()


def clean_trailing_periods_from_title(Class):
    session = create_new_session()
    objects = session.query(Class).all()

    if objects is not None:
        for obj in objects:
            obj.title = obj.title.rstrip(".")
            session.add(obj)
            session.commit()
            print(f"[SUCCESS] ===> [{obj.id}] {Class.__name__} Cleaned")
    else:
        print(f"[ERROR] ===> [{obj.id}] Something went wrong")

    session.close()


def clip_chapter_title_lengths(chapter_id):
    """ For some reason we have chapter titles that are the whole body of the chapter """
    session = create_new_session()
    chapter = session.query(BookChapter).filter_by(id=chapter_id).first()

    if chapter is not None:
        if len(chapter.title) > 64:
            chapter.title = f"{chapter.title[:64]} (...)"
            session.add(chapter)
            session.commit()
            print(f"[SUCCESS] ===> [{chapter.id}] Chapter Cleaned")
    else:
        print(f"[ERROR] ===> [{chapter.id}] Something went wrong")

    session.close()


def clip_book_chapter_titles(book_id):
    session = create_new_session()
    book = session.query(Book).filter_by(id=book_id).first()

    if book is not None:
        volumes = session.query(BookVolume).filter_by(book_id=book.id).order_by(BookVolume.sequence).all()

        if volumes is not None:
            for vol in volumes:
                chapters = session.query(BookChapter).filter_by(volume_id=vol.id).order_by(BookChapter.sequence).all()

                if chapters is not None:
                    for chapter in chapters:
                        clip_chapter_title_lengths(chapter.id)

    session.close()
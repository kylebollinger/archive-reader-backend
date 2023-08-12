import re
from urllib.parse import urljoin

from models import Book, BookVolume, BookChapter, create_new_session

def clean_imported_body(Chapter):
    session = create_new_session()
    body = Chapter.body
    body = re.sub(r"\\n", "", body)
    body = re.sub(r"\\'", "'", body)
    Chapter.body = body
    session.commit()
    session.close()


def update_img_href_body(Chapter):
    session = create_new_session()
    body = Chapter.body
    tag_pattern = r'<a[^>]* href="([^"]*)"[^>]*>'
    tags = re.findall(tag_pattern, body)

    url_key = None
    if Chapter.import_data:
        url_key = Chapter.import_data.get("chap_url").rsplit('/', 1)[0]

    if tags and url_key:
        for tag in tags:
            if tag.startswith('img/'):
                url_path = urljoin(url_key, tag)
                body = body.replace(tag, url_path)

        Chapter.body = body
        session.commit()
    session.close()


def update_imgsrc_body(Chapter):
    session = create_new_session()
    body = Chapter.body
    tag_pattern = r'<img[^>]* src="([^"]*)"[^>]*>'
    tags = re.findall(tag_pattern, body)
    url_key = None
    if Chapter.import_data:
        url_key = Chapter.import_data["chap_url"].rsplit('/', 1)[0]

    if tags and url_key:
        for tag in tags:
            if tag.startswith(url_key):
                return
            url_path = urljoin(url_key, tag)
            body = body.replace(tag, url_path)

        Chapter.body = body
        session.commit()

    session.close()




def bulk_process_books(book_ids):
    session = create_new_session()
    books = session.query(Book).filter(Book.id.in_(book_ids)).all()

    for book in books:
        print(book.import_data.get('web_url'))
        reprocess_single_book()


    session.close()

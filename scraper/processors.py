import re
from urllib.parse import urljoin

from core.models import Book, BookVolume, BookChapter, create_new_session
from scraper.utils import getHTMLdocument, generate_slug_id


def post_process_body(chapter_id):
    session = create_new_session()
    chapter = session.query(BookChapter).filter_by(id=chapter_id).first()
    clean_imported_body(chapter)
    session.commit()
    session.close()


def clean_imported_body(Chapter):
    body = Chapter.body
    body = re.sub(r"\\n", "", body)
    body = re.sub(r"\\'", "'", body)
    Chapter.body = body


def update_img_href_body(Chapter):
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


def update_imgsrc_body(Chapter):
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


def create_base_volume(book):
    # Create a new BookVolume instance
    session = create_new_session()
    base_volume = session.query(BookVolume).filter_by(book_id=book.id).all()

    if not base_volume:
        base_volume = BookVolume(
            title="Contents",
            book_id=book.id,
            sequence=1,
            import_data={
                "vol_id": generate_slug_id(),
                "book_url": book.import_data.get('web_url'),
                "vol_title": "Contents",
                "vol_sequence": 1,
                "vol_url": book.import_data.get('web_url')
            }
        )
        session.add(base_volume)
        session.commit()

    session.close()
    return base_volume


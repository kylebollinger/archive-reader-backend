import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from db.models import Book, BookVolume, BookChapter, create_new_session
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
    base_volume = session.query(BookVolume).filter_by(book_id=book.id).first()

    if base_volume is None:
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
        base_volume = session.query(BookVolume).filter_by(book_id=book.id).first()

    session.close()
    return base_volume


def clean_center_tags(chapter_body):
    soup = BeautifulSoup(chapter_body, "html.parser")

    """ Knock out Footer """
    if soup.select('hr + center'):
        center_tag = soup.select_one('hr + center')
        if len(center_tag.find_next_siblings()) == 0:
            center_tag.find_previous_sibling('hr').decompose()
            center_tag.decompose()

    """ Search and destroy header/footer fallback """
    for center_tag in soup.find_all('center'):
        if center_tag.find_previous_siblings('hr') or center_tag.find_next_siblings('hr'):
            if center_tag.find_previous_sibling('hr'):
                center_tag.find_previous_sibling('hr').decompose()
            if center_tag.find_next_siblings('hr'):
                center_tag.find_next_sibling('hr').decompose()
            center_tag.decompose()
        center_tag.decompose()

    """ Look for sub headers """
    if soup.find_all('p', align="CENTER"):
        # NOTE I think they do an <h3> tag as well
        for centered_p in soup.find_all('p', align="CENTER"):
            if centered_p.find_previous_siblings('hr') or centered_p.find_next_siblings('hr'):
                if centered_p.find_previous_sibling('hr'):
                    centered_p.find_previous_sibling('hr').decompose()
                if centered_p.find_next_siblings('hr'):
                    centered_p.find_next_sibling('hr').decompose()
                centered_p.decompose()

    """ If the first link is available for TOC, try to delete previous"""
    if soup.find(attrs={"name": re.compile("page")}):
        first_p = soup.find(attrs={"name": re.compile("page")})
        header_trash_tags = first_p.parent.find_previous_siblings()
        for tag in header_trash_tags:
            tag.decompose()


    body_tag = soup.find('body')
    return body_tag

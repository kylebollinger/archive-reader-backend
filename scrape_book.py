from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests, csv, re, string, secrets, time, random
import sys, os

from models import Book, BookVolume, BookChapter, create_new_session
from scraper.utils import getHTMLdocument, generate_slug_id, root_url


session = create_new_session()

# book = session.query(Book).filter_by(id=274).first()
# book = session.query(Book).filter_by(id=280).first() # has wikipedia link in middle of text
book = session.query(Book).filter_by(id=296).first()


def create_base_volume(book):
    # Create a new BookVolume instance
    base_volume = BookVolume(
        title="Contents",
        book_id=book.id,
        sequence=1,
        data={},
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

    return base_volume


def fetch_chapter_body_data(chapter_page_url):
    time.sleep(1.5)
    html_doc, encoding = getHTMLdocument(chapter_page_url)
    soup = BeautifulSoup(html_doc, "html.parser")
    body_tag = soup.find('body')

    print(chapter_page_url, encoding)

    if soup.find(attrs={"name": re.compile("page")}):
        first_p = soup.find(attrs={"name": re.compile("page")})
        header_trash_tags = first_p.parent.find_previous_siblings()
        for tag in header_trash_tags:
            tag.decompose()

        if soup.select('hr + center'):
            center_tag = soup.select_one('hr + center')
            if len(center_tag.find_next_siblings()) == 0:
                center_tag.find_previous_sibling('hr').decompose()
                center_tag.decompose()

    return body_tag


def scrape_volumes(book):
    book_url = book.import_data.get('web_url')
    html_doc, encoding = getHTMLdocument(book_url)
    soup = BeautifulSoup(html_doc, "html.parser")
    volumes = session.query(BookVolume).filter_by(book_id=book.id).all()

    # Delete all center tags
    for center_tag in soup.find_all('center'):
        center_tag.decompose()

    if len(soup.find_all('a')) > 0 and not volumes:
        """ Time to create a base volume and extract chapters """
        chap_sequence = 0
        # base_volume = create_base_volume(book)

        # Then Find all the link tags
        for link_tag in soup.find_all('a'):
            """ After removing all the <center> tags with links, the remaining <a> tags are the ones we want for the chapters

                chapter_titles ==> link_tag.text
                chapter_urls   ==> link_tag.get('href')
            """
            if "http" in link_tag.get('href'):
                """ Not internal link, cant be a chapter """
                continue

            chap_sequence += 1

            if link_tag.find_next_sibling('a') or link_tag.find_previous_sibling('a'):
                """ This should be link in a list of chapters """
                chapter_url = f"{book_url.rsplit('/', 1)[0]}/{link_tag.get('href')}"
                chapter_body = fetch_chapter_body_data(chapter_url)

                # Create a new BookChapter instance




scrape_volumes(book)
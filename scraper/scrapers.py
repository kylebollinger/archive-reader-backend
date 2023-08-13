import os, time, re
from bs4 import BeautifulSoup
from core.models import Book, BookVolume, BookChapter, create_new_session

from scraper.utils import getHTMLdocument, generate_slug_id, remove_byte_encoding
from scraper.processors import create_base_volume, post_process_body
from core.helpers import clean_filename

def scrape_chapter(chapter_page_url):
    time.sleep(1.5)
    html_doc, encoding = getHTMLdocument(chapter_page_url)
    soup = BeautifulSoup(html_doc, "html.parser")
    print(chapter_page_url, encoding)

    """ Knock out Footer """
    if soup.select('hr + center'):
        center_tag = soup.select_one('hr + center')
        if len(center_tag.find_next_siblings()) == 0:
            center_tag.find_previous_sibling('hr').decompose()
            center_tag.decompose()

    """ Search and destroy fallback header and footer """
    for center_tag in soup.find_all('center'):
        center_tag.decompose()

    """ Look for sub headers """
    if soup.find_all('p', align="CENTER"):
        for centered_p in soup.find_all('p', align="CENTER"):
            if centered_p.find_previous_siblings('hr') or centered_p.find_next_siblings('hr'):
                if centered_p.find_previous_sibling('hr'):
                    centered_p.find_previous_sibling('hr').decompose()
                if centered_p.find_next_siblings('hr'):
                    centered_p.find_next_sibling('hr').decompose()
                centered_p.decompose()


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

    body_tag = soup.find('body')
    return body_tag


def scrape_book(book_id):
    session = create_new_session()
    book = session.query(Book).filter_by(id=book_id).first()
    book_url = book.import_data.get('web_url')
    html_doc, encoding = getHTMLdocument(book_url)
    soup = BeautifulSoup(html_doc, "html.parser")

    # Delete all center tags
    for center_tag in soup.find_all('center'):
        center_tag.decompose()

    if len(soup.find_all('a')) > 0:
        """ Time to create a base volume and extract chapters """
        chap_sequence = 0

        volumes = session.query(BookVolume).filter_by(book_id=book.id).all()
        if len(volumes) == 0:
            base_volume = create_base_volume(book)
        elif len(volumes) == 1:
            base_volume = volumes[0]
        else:
            print("ERROR: More than one volume found for book")
            # sys.exit()

        # Then Find all the link tags
        for link_tag in soup.find_all('a'):
            """ After removing all the <center> tags with links, the remaining <a> tags are the ones we want for the chapters

                chapter_titles ==> link_tag.text
                chapter_urls   ==> link_tag.get('href')
            """
            if link_tag.get('href') and "http" in link_tag.get('href'):
                """ Not internal link, cant be a chapter """
                continue

            chap_sequence += 1

            if link_tag.find_next_sibling('a') or link_tag.find_previous_sibling('a'):
                """ This should be link in a list of chapters """
                chapter_title = clean_filename(link_tag.text)
                chapter_url = f"{book_url.rsplit('/', 1)[0]}/{link_tag.get('href')}"
                chapter_body = scrape_chapter(chapter_url)

                encoded_body = chapter_body.encode(formatter="html5")
                chapter_body = remove_byte_encoding(str(encoded_body))

                # Create a new BookChapter instance
                new_chapter = BookChapter(
                    title=chapter_title,
                    volume_id=base_volume.id,
                    sequence=chap_sequence,
                    book_sequence=chap_sequence,
                    body=chapter_body,
                    import_data={
                        "chap_url": chapter_url,
                        "chap_title": chapter_title,
                        "chap_sequence": chap_sequence,
                        "chap_body_size": len(chapter_body)
                    }
                )
                session.add(new_chapter)
                session.commit()

                post_process_body(new_chapter.id)

    session.close()


def bulk_scrape_books(book_ids):
    session = create_new_session()
    books = session.query(Book).filter(Book.id.in_(book_ids)).all()

    for book in books:
        scrape_book(book.id)

    session.close()


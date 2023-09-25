import os, time, re, requests
from bs4 import BeautifulSoup
from db.models import Book, BookVolume, BookChapter, create_new_session

from scraper.processors import (
    create_base_volume,
    post_process_body,
    clean_center_tags
)

from scraper.utils import (
    OUTPUT_DIR,
    register_base_dirs,
    save_file,
    scrub_filename,
    clean_filename,
    getHTMLdocument,
    remove_byte_encoding
)


def scrape_chapter(chapter_page_url):
    time.sleep(1.5)
    html_doc, encoding = getHTMLdocument(chapter_page_url)
    clean_center_tags(html_doc)


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

                if chapter_body:
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

    total_count = len(books)
    processed_count = 0
    for book in books:
        scrape_book(book.id)
        processed_count += 1
        print(f"Processed Book [{book.id}] =====> {processed_count} of {total_count}")

    session.close()


def bulk_process_books():
    """
        This function is used to process the current db that was previously scraped with some errors. Rather than rescraping the entire db, this will assess and reprocess the books that have already been scraped. It should not need to be used again in the future.
    """
    session = create_new_session()
    register_base_dirs()

    # Go grab all the books
    books = session.query(Book).limit().all()
    unprocessed_books = []
    rescrape_books = []

    for book in books:
        volumes = session.query(BookVolume).filter_by(book_id=book.id).order_by(BookVolume.sequence).all()
        volume_ids = [volume.id for volume in volumes]
        full_book_dir = f"{OUTPUT_DIR}/books"

        if len(volumes) > 0:
            """ Book was originally scraped correctly and has volumes """
            book_content_html = ""
            book_file_name = scrub_filename(book.title)
            chap_book_dir = f"{OUTPUT_DIR}/chapters/[{book.id}] {book_file_name}"
            os.makedirs(chap_book_dir, exist_ok=True)

            for volume in volumes:
                chapters = session.query(BookChapter).filter_by(volume_id=volume.id).order_by(BookChapter.sequence).all()
                chapter_ids = [chapter.id for chapter in chapters]
                print(f"[{book.id}] ==> ({len(chapter_ids)}) Chapters to process")

                for chapter in chapters:
                    book_content_html += f"\n\n{chapter.body}\n\n"
                    soup = BeautifulSoup(chapter.body, 'html.parser')
                    book_content_txt = soup.get_text()
                    file_name = f"[{chapter.book_sequence}] {chapter.title}"

                    # Save html & plain txt chapter
                    save_file(file_name, chapter.body, 'html', chap_book_dir)
                    save_file(file_name, book_content_txt, 'txt', chap_book_dir)


            # Save full book
            book_filename = f"[{book.id}] {book.title}"
            soup = BeautifulSoup(book_content_html, 'html.parser')
            book_content_txt = soup.get_text()

            # Save html & plain txt concatenated book
            save_file(book_filename, book_content_html, 'html', full_book_dir)
            save_file(book_filename, book_content_txt, 'txt', full_book_dir)
            print(f"[{book.id}] ==> Page downloaded --> [SUCCESS]")

        elif book.state == 'initialized' and book.import_data.get('web_url'):
            """ If a book has no volumes, it can be one of a few things:
                1 ==> It is a link to download a .txt file
                2 ==> It is a book with no volumes and rendered on a single page
                3 ==> There was an error in scraping the first time
            """
            download_url = book.import_data.get('web_url')
            if book.import_data.get('format') == 'text':
                """ Option 1 Processer"""
                if download_url:
                    response = requests.get(download_url)
                    if response.status_code == 200:
                        book_filename = f"[{book.id}] {book.title}"
                        save_file(book_filename, response.text, 'txt', full_book_dir)
                        print(f"[{book.id}] ==> File downloaded --> [SUCCESS]")
                    else:
                        unprocessed_books.append(book.id)
                        print(f"[{book.id}] ==> File downloaded --> [FAILED]")
                    print(f"Attempted ==> {book.import_data.get('web_url')}")
                else:
                    unprocessed_books.append(book.id)
            else:
                """ Option 2|3 Processer """
                if download_url:
                    response = requests.get(download_url)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Delete all center tags (Header and Footer)
                        for center_tag in soup.find_all('center'): center_tag.decompose()

                        if len(soup.find_all('a')) > 0:
                            # Look for a structure that resembles table of contents
                            run_scraper = False
                            for link_tag in soup.find_all('a'):
                                if link_tag.find_next_sibling('a') or link_tag.find_previous_sibling('a'):
                                    run_scraper = True
                            if run_scraper:
                                """ Option #3:
                                An error occured while trying to scrape the first time
                                """
                                # NOTE This could kick off a scraper function instead of collecting the ids and running it as a bulk operation.
                                rescrape_books.append(book.id)

                        else:
                            """ Option 2:
                                Single book rendered on a single page
                            """
                            book_filename = f"[{book.id}] {book.title}"
                            book_content_html = str(soup)
                            book_content_txt = soup.get_text()

                            # Save html & plain txt concatenated book
                            save_file(book_filename, book_content_html, 'html', full_book_dir)
                            save_file(book_filename, book_content_txt, 'txt', full_book_dir)
                            print(f"[{book.id}] ==> Page downloaded --> [SUCCESS]")
                    else:
                        unprocessed_books.append(book.id)
                        print(f"[{book.id}] ==> Page unreachable --> [FAILED]")
                else:
                    unprocessed_books.append(book.id)


    # Print out the results
    print(f"\n\n=========================================\n"
        f"Total books ==> {len(books)}\n"
        f"Unprocessed books ==> {len(unprocessed_books)}\n"
        f"{unprocessed_books}\n"
        f"Books to Rescrape ==> {len(rescrape_books)}\n"
        f"{rescrape_books}\n")
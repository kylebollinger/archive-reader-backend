import os, requests
from bs4 import BeautifulSoup

from db.models import Book, BookVolume, BookChapter, create_new_session
from core.helpers import (
    OUTPUT_DIR,
    register_base_dirs,
    save_file,
    scrub_filename
)


session = create_new_session()
register_base_dirs()

# Go grab all the books
books = session.query(Book).limit().all()
# books = session.query(Book).filter_by(id=1028).all()
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
import os, requests
from bs4 import BeautifulSoup

from models import User, Book, BookVolume, BookCategory, BookChapter, create_new_session
from helpers import clean_filename


session = create_new_session()

# Initialize Output Directories
OUTPUT_DIR = "outputs"
dir_paths = [OUTPUT_DIR, f"{OUTPUT_DIR}/txt", f"{OUTPUT_DIR}/html"]

for dir_path in dir_paths:
    os.makedirs(dir_path, exist_ok=True)


# Go grab all the books

books = session.query(Book).all()
unprocessed_books = []

for book in books:
    book_title = clean_filename(book.title)
    volumes = session.query(BookVolume).filter_by(book_id=book.id).order_by(BookVolume.sequence).all()
    volume_ids = [volume.id for volume in volumes]

    if len(volumes) > 0:
        """ Book was originally scraped correctly and has volumes """
        book_content_html = ""
        for volume in volumes:
            chapters = session.query(BookChapter).filter_by(volume_id=volume.id).order_by(BookChapter.sequence).all()
            chapter_ids = [chapter.id for chapter in chapters]
            print(f"[{book.id}] ==> ({len(chapter_ids)}) Chapters to process")

            for chapter in chapters:
                book_content_html += f"{chapter.title}\n\n{chapter.body}\n\n"

        # Save html concatenated book
        file_path_html = os.path.join(OUTPUT_DIR, 'html', book_title)
        with open(f"{file_path_html}.txt", "a") as file:
            file.write(book_content_html)

        # Save plain txt concatenated book
        file_path_txt = os.path.join(OUTPUT_DIR, 'txt', book_title)
        soup = BeautifulSoup(book_content_html, 'html.parser')
        book_content_txt = soup.get_text()
        with open(f"{file_path_txt}.txt", "a") as file:
            file.write(book_content_txt)
    elif book.state == 'initialized' and book.import_data.get('web_url'):
        """ If a book has no volumes, it can be one of two things:
            1 ==> It is a link to download a .txt file
            2 ==> It is a book with no volumes and listed on a single page
        """
        download_url = book.import_data.get('web_url')
        if book.import_data.get('format') == 'text':
            """ Option 1 """
            if download_url:
                response = requests.get(download_url)

                if response.status_code == 200:
                    file_path = os.path.join(OUTPUT_DIR, 'txt', book_title)
                    with open(f"{file_path}.txt", "wb") as file:
                        file.write(response.content)
                    print(f"[{book.id}] ==> File downloaded --> [SUCCESS]")
                else:
                    unprocessed_books.append(book.id)
                    print(f"[{book.id}] ==> File downloaded --> [FAILED]")
                print(f"Download attempt ==> {book.import_data.get('web_url')}")
            else:
                unprocessed_books.append(book.id)
        else:
            """ Option 2 """
            if download_url:
                response = requests.get(download_url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Save html concatenated book
                    file_path_html = os.path.join(OUTPUT_DIR, 'html', book_title)
                    with open(f"{file_path_html}.txt", "a") as file:
                        file.write(str(soup))

                    # Save plain txt concatenated book
                    file_path_txt = os.path.join(OUTPUT_DIR, 'txt', book_title)
                    book_content_txt = soup.get_text()
                    with open(f"{file_path_txt}.txt", "a") as file:
                        file.write(book_content_txt)

                    print(f"[{book.id}] ==> Page downloaded --> [SUCCESS]")
                else:
                    unprocessed_books.append(book.id)
                    print(f"[{book.id}] ==> Page downloaded --> [FAILED]")
            else:
                unprocessed_books.append(book.id)
            unprocessed_books.append(book.id)



print("\n\n=========================================\n")
print(f"Total books ==> {len(books)}")
print(f"Unprocessed books ==> {len(unprocessed_books)}")
print(unprocessed_books)
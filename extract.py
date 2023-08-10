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

for book in books:
    book_content_html = ""
    book_title = clean_filename(book.title)

    if book.state == 'initialized':
        """
            Check if book has volumes, if not this is probably
            a text only book. Let's download it and save it
        """
        if book.import_data.get('format') == 'text':
            download_url = book.import_data.get('web_url')
            if download_url:
                response = requests.get(download_url)

                if response.status_code == 200:
                    file_path = os.path.join(OUTPUT_DIR, 'txt', book_title)
                    with open(f"{file_path}.txt", "wb") as file:
                        file.write(response.content)
                    print(f"[{book.id}] ==> File downloaded --> [SUCCESS]")
                else:
                    print(f"[{book.id}] ==> File downloaded --> [FAILED]")
                print(f"Download attempt ==> {book.import_data.get('web_url')}")

    else:
        volumes = session.query(BookVolume).filter_by(book_id=book.id).order_by(BookVolume.sequence).all()
        volume_ids = [volume.id for volume in volumes]
        print(f"[{book.id}] ==> ({len(volume_ids)}) Volumes to tackle --> {volume_ids}")

        for volume in volumes:
            if len(volumes) > 0:
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
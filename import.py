import os
import mysql.connector
# from bs4 import BeautifulSoup

# Connect to your MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="xdev"
)

# Create a cursor
cursor = db_connection.cursor()

# Fetch data from the database (example query, modify as needed)
query = "SELECT books.id, books.title, book_volumes.id, book_volumes.title, book_chapters.sequence, book_chapters.body " \
        "FROM books " \
        "JOIN book_volumes ON books.id = book_volumes.book_id " \
        "JOIN book_chapters ON book_volumes.id = book_chapters.volume_id " \
        "LIMIT 100"

cursor.execute(query)
results = cursor.fetchall()

# Close the database connection
db_connection.close()

# Create a directory to store the text files
OUTPUT_DIR = "output_books"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_book(file_name, book_text):
    # Write the chapter content to the text file
    print("saving book")
    file_path = os.path.join(OUTPUT_DIR, file_name)
    with open(file_path, "a") as file:
        file.write(book_text)

current_book = 0
book_text = ""

# Loop through the results
for result in results:
    book_id, book_title, volume_id, volume_title, sequence, chapter_body = result
    file_name = f"{book_id} - {book_title} - {volume_id}.txt"

    # Add chapters to the book_text
    while result and result[0] == book_id:
        chapter_sequence, chapter_body = result[4], result[5]
        book_text += f"Chapter {chapter_sequence}\n\n{chapter_body}\n\n"
        result = cursor.fetchone()  # Move to the next result

    # Save the book text to a file
    save_book(file_name, book_text)

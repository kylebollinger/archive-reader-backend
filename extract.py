from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy import Enum
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import requests, os
import pymysql

pymysql.install_as_MySQLdb()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))
    photo = Column(String(255))
    website = Column(String(255))
    job_title = Column(String(255))
    role = Column(Enum('admin', 'user', name='user_role'), default='user')
    course_created = Column(Integer, default=0)
    course_purchased = Column(Integer, default=0)
    status = Column(Enum('active', 'inactive'), default='active')
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    bio = Column(Text)
    remember_token = Column(Text)

    books = relationship("Book", back_populates="user")

class Book(Base):
    __tablename__ = 'books'
    __table_args__ = {'mysql_collate': 'utf8mb3_unicode_ci'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    subtitle = Column(String(255))
    author = Column(String(255))
    slug = Column(String(255), unique=True)
    cover = Column(String(255))
    publish_date = Column(DateTime)
    description = Column(Text())
    data = Column(JSON)
    import_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('book_categories.id'))
    state = Column(String(255), nullable=False, default='initialized')

    user = relationship('User', back_populates='books')
    category = relationship('BookCategory', back_populates='books')
    user = relationship("User", back_populates="books")
    volumes = relationship("Volume", back_populates="book")


class BookVolume(Base):
    __tablename__ = 'book_volumes'
    __table_args__ = {'mysql_collate': 'utf8mb3_unicode_ci'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    sequence = Column(Integer)
    data = Column(JSON)
    import_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    book = relationship('Book', back_populates='volumes')
    chapters = relationship('BookChapter', back_populates='volume')
    book = relationship("Book", back_populates="volumes")

class BookCategory(Base):
    __tablename__ = 'book_categories'
    __table_args__ = {'mysql_collate': 'utf8mb3_unicode_ci'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    slug = Column(String(255), unique=True)
    description = Column(Text())
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    books = relationship('Book', back_populates='category')

class BookChapter(Base):
    __tablename__ = 'book_chapters'
    __table_args__ = {'mysql_collate': 'utf8mb3_unicode_ci'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    volume_id = Column(Integer, ForeignKey('book_volumes.id'), nullable=False)
    sequence = Column(Integer)
    book_sequence = Column(Integer)
    title = Column(Text())
    body = Column(Text())
    data = Column(JSON)
    import_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define the relationship to Volume
    volume = relationship('BookVolume', back_populates='chapters')


Book.volumes = relationship("BookVolume", back_populates="book")
BookVolume.book = relationship('Book', back_populates='volumes')

engine = create_engine('mysql://root:@localhost/xdev')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


# Initialize Output Directory
OUTPUT_DIR = "output_books"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Go grab all the books
books = session.query(Book).limit(200).all()

for book in books:
    if book.state == 'initialized':
        """
            Check if book has volumes, if not this is probably
            a text only book. Let's download it and save it
        """
        if book.import_data.get('format') == 'text':
            print("lets download this book")
            download_url = book.import_data.get('web_url')
            if download_url:
                response = requests.get(download_url)

                if response.status_code == 200:
                    # TODO Clean the title
                    file_path = os.path.join(OUTPUT_DIR, book.title)
                    with open(f"{file_path}.txt", "wb") as file:
                        file.write(response.content)
                    print("File downloaded successfully.")
                else:
                    print("Failed to download the file.")
                print(f"Download attempt from: {book.import_data.get('web_url')}")

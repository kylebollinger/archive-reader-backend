import psycopg2
from sqlalchemy import Enum
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import requests, os

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column, Integer, String,
    Text, JSON, DateTime,
    ForeignKey
)

load_dotenv()
Base = declarative_base()


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
    data = Column(JSON, nullable=True)
    import_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    category_id = Column(Integer, ForeignKey('book_categories.id'))
    state = Column(String(255), nullable=False, default='initialized')

    category = relationship('BookCategory', back_populates='books')
    volumes = relationship("Volume", back_populates="book")

    def __repr__(self):
        return f"Book(id={self.id}, title='{self.title}')"


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


    def __repr__(self):
        return f"BookVolume(id={self.id}, title='{self.title}', book_id={self.book_id}, sequence={self.sequence})"


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

    def __repr__(self):
        return f"BookChapter(id={self.id}, volume_id={self.volume_id} title='{self.title}', sequence={self.sequence}, book_sequence={self.book_sequence})"

    def __len__(self):
        soup = BeautifulSoup(self.body, 'html.parser')
        length = soup.get_text()
        return len(length)


Book.volumes = relationship("BookVolume", back_populates="book")
BookVolume.book = relationship('Book', back_populates='volumes')


def create_new_session():
    driver = os.environ.get('DB_DRIVER', 'postgresql+psycopg2')
    username = os.environ.get('DB_USERNAME', 'xero')
    password = os.environ.get('DB_PASSWORD', 'xeropoint')
    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '5432')
    database = os.environ.get('DB_DATABASE', 'xeropoint')

    db_config = f"{driver}://{username}:{password}@{host}:{port}/{database}"
    engine = create_engine(db_config)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()

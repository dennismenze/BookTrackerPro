from models import db, Author, Book, UserBook, BookList, User
import sys	

from app import create_app
from utils import fetch_google_books_info, get_author_image_from_wikimedia

app = create_app()

with app.app_context():
    cnt = 0
    authors = Author.query.all()
    for author in authors:
        author.image_url = get_author_image_from_wikimedia(author.name)
        cnt += 1
        if cnt % 50 == 0:
            db.session.commit()

    db.session.commit()

    cnt = 0
    books = Book.query.all()
    for book in books:
        if not book.cover_image_url:
            book_info = fetch_google_books_info(book.title, book.author.name)
            if book_info:
                book.cover_image_url = book_info['cover_image_url']
                book.description = book_info['description']
                book.page_count = book_info['page_count']
                book.published_date = book_info['published_date']
                book.isbn = book_info['isbn']
                cnt += 1
                if cnt % 50 == 0:
                    db.session.commit()

    db.session.commit()

    print("Author and book data has been updated.")
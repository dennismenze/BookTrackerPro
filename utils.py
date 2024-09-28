from models import db, Author, Book, UserBook, BookList
from flask import current_app
import requests


def calculate_read_percentage(books, user_id):
    if not books:
        return 0
    read_books = sum(1 for book in books if is_book_read(book, user_id))
    return (read_books / len(books)) * 100


def calculate_read_main_works_percentage(books, user_id):
    main_works = [book for book in books if book.is_main_work]
    if not main_works:
        return 0
    return calculate_read_percentage(main_works, user_id)


def get_books_stats(books, user_id):
    read_books = sum(1 for book in books if is_book_read(book, user_id))
    main_works = [book for book in books if book.is_main_work]
    read_main_works = sum(1 for book in main_works
                          if is_book_read(book, user_id))
    return {
        'total_books':
        len(books),
        'read_books':
        read_books,
        'read_percentage':
        calculate_read_percentage(books, user_id),
        'total_main_works':
        len(main_works),
        'read_main_works':
        read_main_works,
        'read_main_works_percentage':
        calculate_read_main_works_percentage(books, user_id)
    }


def is_book_read(book, user_id):
    user_book = UserBook.query.filter_by(user_id=user_id,
                                         book_id=book.id).first()
    return user_book.is_read if user_book else False

def map_author_data(author, user_id):  
    books = [map_book_data(book, user_id) for book in author.books]
    book_stats = get_books_stats(author.books, user_id)    
    
    author_data = {
        'id': author.id,
        'name': author.name,
        'image_url': author.image_url,
        'books': books,
        'total_books': book_stats['total_books'],
        'read_books': book_stats['read_books'],
        'read_percentage': book_stats['read_percentage'],
        'total_main_works': book_stats['total_main_works'],
        'read_main_works': book_stats['read_main_works'],
        'read_main_works_percentage': book_stats['read_main_works_percentage']
    }

    if not author.image_url:
        author.image_url = get_author_image_from_wikimedia(author.name)
        db.session.commit()
    return author_data

def get_author_image_from_wikimedia(author_name):
    # Definiere die API-Endpunkt-URL
    url = "https://en.wikipedia.org/w/api.php"

    # Parameter für die Wikipedia-API, um die Seite des Autors zu suchen
    params = {
        "action": "query",
        "titles": author_name,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 500  # Die Größe des gewünschten Thumbnails in Pixeln
    }

    # Anfrage an die Wikipedia-API senden
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Extrahiere die Bild-URL aus der Antwort
    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if "thumbnail" in page:
            return page["thumbnail"]["source"]

    return None

def map_book_data(book, user_id):
    book_data = {
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'author_id': book.author_id,
        'is_read': is_book_read(book, user_id),
        'is_main_work': book.is_main_work,
        'cover_image_url': book.cover_image_url
        or '/static/images/no-cover.png',
        'isbn': book.isbn,
        'description': book.description,
        'page_count': book.page_count,
        'published_date': book.published_date,
        'lists': []
    }

    if not all([
            book.isbn, book.description, book.cover_image_url, book.page_count,
            book.published_date
    ]):
        google_books_info = fetch_google_books_info(book.title,
                                                    book.author.name)

        book_data['isbn'] = book.isbn or google_books_info.get('isbn')
        book_data['description'] = book.description or google_books_info.get(
            'description')
        book_data[
            'cover_image_url'] = book.cover_image_url or google_books_info.get(
                'cover_image_url')
        book_data['page_count'] = book.page_count or google_books_info.get(
            'page_count')
        book_data[
            'published_date'] = book.published_date or google_books_info.get(
                'published_date')

        book.isbn = book_data['isbn']
        book.description = book_data['description']
        book.cover_image_url = book_data['cover_image_url']
        book.page_count = book_data['page_count']
        book.published_date = book_data['published_date']

        db.session.commit()
    return book_data


def fetch_google_books_info(title, author):
    try:
        query = f"intitle:{title}+inauthor:{author}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(url)
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            volume_info = data['items'][0]['volumeInfo']
            return {
                'isbn':
                volume_info.get('industryIdentifiers',
                                [{}])[0].get('identifier'),
                'description':
                volume_info.get('description'),
                'cover_image_url':
                volume_info.get('imageLinks', {}).get('thumbnail'),
                'page_count':
                volume_info.get('pageCount'),
                'published_date':
                volume_info.get('publishedDate')
            }
        else:
            return {}
    except Exception as e:
        current_app.logger.error(f"Error fetching Google Books info: {str(e)}")
        return {}

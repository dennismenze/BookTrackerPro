from models import db, Author, Book, UserBook, BookList, Translation
from flask import current_app
import requests
from typing import Dict, Any, Optional
import csv
import io
from datetime import datetime


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


def fetch_google_books_info(title: str, author: str) -> Optional[Dict[str, Any]]:
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"intitle:{title}+inauthor:{author}",
        "langRestrict": "en",
        "maxResults": 1
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("totalItems", 0) > 0:
            volume_info = data["items"][0]["volumeInfo"]
            book_info = {
                'isbn': volume_info.get('industryIdentifiers', [{}])[0].get('identifier'),
                'description_en': volume_info.get('description', ''),
                'cover_image_url': volume_info.get('imageLinks', {}).get('thumbnail'),
                'page_count': volume_info.get('pageCount'),
                'published_date': volume_info.get('publishedDate')
            }

            # Fetch German version
            params["langRestrict"] = "de"
            response_de = requests.get(base_url, params=params)
            response_de.raise_for_status()
            data_de = response_de.json()

            if data_de.get("totalItems", 0) > 0:
                volume_info_de = data_de["items"][0]["volumeInfo"]
                book_info['description_de'] = volume_info_de.get('description', '')
                book_info['title_de'] = volume_info_de.get('title', '')
                book_info['cover_image_url_de'] = volume_info_de.get('imageLinks', {}).get('thumbnail', '')

            return book_info
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching book info: {e}")
        return None


def fetch_google_authors_info(author_name: str) -> Optional[Dict[str, Any]]:
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"inauthor:{author_name}",
        "langRestrict": "en",
        "maxResults": 1
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("totalItems", 0) > 0:
            volume_info = data["items"][0]["volumeInfo"]
            author_info = {
                "name": author_name,
                "biography_en": volume_info.get("description", ""),
                "image_url": volume_info.get("imageLinks", {}).get("thumbnail", "")
            }

            # Fetch German version
            params["langRestrict"] = "de"
            response_de = requests.get(base_url, params=params)
            response_de.raise_for_status()
            data_de = response_de.json()

            if data_de.get("totalItems", 0) > 0:
                volume_info_de = data_de["items"][0]["volumeInfo"]
                author_info['name_de'] = volume_info_de.get("title", "")
                author_info['biography_de'] = volume_info_de.get("description", "")

            return author_info
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching author info: {e}")
        return None

def fetch_openlibrary_books_info(title: str, author: str) -> Optional[Dict[str, Any]]:
    search_url = "https://openlibrary.org/search.json"
    search_params = {
        "title": title,
        "author": author,
        "limit": 1
    }

    try:
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()

        if search_data.get("numFound", 0) > 0:
            work_key = search_data["docs"][0].get("key")
            if not work_key:
                return None

            book_info = {}

            # Suche nach der deutschen Edition
            editions_url = f"https://openlibrary.org/works/{work_key}/editions.json"
            editions_response = requests.get(editions_url)
            editions_response.raise_for_status()
            editions_data = editions_response.json()

            for edition in editions_data.get('entries', []):
                if edition.get('languages') and any(lang.get('key') == '/languages/ger' for lang in edition['languages']):
                    book_info['title_de'] = edition.get('title', '')
                    break

            return book_info
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching book info from OpenLibrary: {e}")
        return None

def process_csv(csv_file, mappings, user):
    """
    Verarbeitet die hochgeladene CSV-Datei basierend auf den Zuordnungen und importiert die Bücher für den Benutzer.

    :param csv_file: Die hochgeladene CSV-Datei
    :param mappings: Ein Dictionary, das die Zuordnung der erforderlichen Felder zu den CSV-Spalten enthält
    :param user: Das aktuelle Benutzerobjekt
    :return: Die Anzahl der erfolgreich importierten Bücher
    """
    try:
        stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream, delimiter=';')  # Passe das Trennzeichen ggf. an

        imported_count = 0
        for row in csv_reader:
            # Verwende die Zuordnungen, um die entsprechenden Felder auszulesen
            title = row.get(mappings.get('title'), '').strip()
            author_name = row.get(mappings.get('author'), '').strip()
            isbn = row.get(mappings.get('isbn'), '').strip()
            read_date_str = row.get(mappings.get('read_date'), '').strip()

            if not title or not author_name:
                continue

            # Suche oder erstelle den Autor
            author = Author.query.filter(Author.name == author_name).first()
            if not author:
                author_translation = Translation(text_en=author_name, text_de=author_name)
                author = Author(name=author_translation)
                db.session.add(author)

            # Suche oder erstelle das Buch
            book = Book.query.filter(
                (Book.title.has(text_en=title)) & 
                (Book.title.has(text_de=title)) & 
                (Book.author == author)
            ).first()
            if not book:
                book_translation = Translation(text_en=title, text_de=title)
                book = Book(title=book_translation, author=author, isbn=isbn)
                db.session.add(book)

            # Verknüpfe das Buch mit dem Benutzer
            user_book = UserBook.query.filter_by(user_id=user.id, book_id=book.id).first()
            if not user_book:
                user_book = UserBook(user_id=user.id, book_id=book.id)
                db.session.add(user_book)

            # Verarbeite das Lese-Datum, falls vorhanden
            if read_date_str:
                try:
                    read_date = datetime.strptime(read_date_str, '%Y-%m-%d').date()
                    user_book.read_date = read_date
                except ValueError:
                    current_app.logger.warning(f"Ungültiges Datumsformat für Buch '{title}': {read_date_str}")

            imported_count += 1

        db.session.commit()
        return imported_count

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Fehler beim Verarbeiten der CSV-Datei: {e}")
        raise e
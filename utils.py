from models import db, Author, Book, UserBook, BookList
from flask import current_app

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
    read_main_works = sum(1 for book in main_works if is_book_read(book, user_id))
    return {
        'total_books': len(books),
        'read_books': read_books,
        'read_percentage': calculate_read_percentage(books, user_id),
        'total_main_works': len(main_works),
        'read_main_works': read_main_works,
        'read_main_works_percentage': calculate_read_main_works_percentage(books, user_id)
    }

def is_book_read(book, user_id):
    user_book = UserBook.query.filter_by(user_id=user_id,
                                         book_id=book.id).first()
    return user_book.is_read if user_book else False

def map_book_data(book, user_id):
    book_data = {
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'author_id': book.author_id,
        'is_read': is_book_read(book, user_id),
        'is_main_work': book.is_main_work,
        'cover_image_url': book.cover_image_url or '/static/images/no-cover.png',
        'isbn': book.isbn,
        'description': book.description,
        'page_count': book.page_count,
        'published_date': book.published_date,
        'lists': []
    }
    
    if not all([book.isbn, book.description, book.cover_image_url, book.page_count, book.published_date]):
            google_books_info = fetch_google_books_info(book.title, book.author.name)
            
            book_data['isbn'] = book.isbn or google_books_info.get('isbn')
            book_data['description'] = book.description or google_books_info.get('description')
            book_data['cover_image_url'] = book.cover_image_url or google_books_info.get('cover_image_url')
            book_data['page_count'] = book.page_count or google_books_info.get('page_count')
            book_data['published_date'] = book.published_date or google_books_info.get('published_date')

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
                'isbn': volume_info.get('industryIdentifiers', [{}])[0].get('identifier'),
                'description': volume_info.get('description'),
                'cover_image_url': volume_info.get('imageLinks', {}).get('thumbnail'),
                'page_count': volume_info.get('pageCount'),
                'published_date': volume_info.get('publishedDate')
            }
        else:
            return {}
    except Exception as e:
        current_app.logger.error(f"Error fetching Google Books info: {str(e)}")
        return {}


import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc

def import_authors_and_books():
    base_url = "https://thegreatestbooks.org/authors"
    pages_to_scrape = 10   

    options = Options()
    #options.add_argument('--headless')  # Optional: Webbrowser im Hintergrund ausführen
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Starte den WebDriver
    driver = uc.Chrome(options=options)

    authors_books = {}

    for page in range(1, pages_to_scrape + 1):
        url = f"{base_url}/page/{page}"
        driver.get(url)
        
        time.sleep(2)  # Warte auf das Laden der Seite
        
        # Finde die Container für Autoren und deren Bücher
        authors = driver.find_elements(By.CLASS_NAME, 'mb-4')
        
        for author in authors:
            author_name = author.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').text.strip()  # Name des Autors
            books = author.find_elements(By.CLASS_NAME, 'default-book-image')  # Container für Bücher
            
            # Füge den Autor und seine Bücher zur Liste hinzu
            author_books = []
            for book in books:
                book_title = book.find_element(By.TAG_NAME, 'img').get_attribute('alt')  # Titel des Buches aus dem alt-Attribut
                book_title = book_title.split(' by ')[0][10:-1]
                author_books.append(book_title)
                
            authors_books[author_name] = author_books

    driver.quit()  # Schließe den WebDriver 

    # Ausgabe der gesammelten Daten
    for authorName, books in authors_books.items():

        # Finde den Autor oder erstelle ihn neu
        author = Author.query.filter_by(name=authorName).first()
        if not author:
            author = Author(name=authorName)
            db.session.add(author)
            db.session.commit()

        for bookName in books:
            # Finde das Buch oder erstelle es neu
            book = Book.query.filter_by(title=bookName, author_id=author.id).first()
            if not book:
                book = Book(
                    title=bookName,
                    author=author,
                    is_main_work=True  # Da wir uns auf die Hauptwerke fokussieren
                )
                db.session.add(book)

    # Änderungen speichern
    db.session.commit()
    print("Daten wurden erfolgreich importiert.")

def clear_authors_and_books():
    # Lösche alle Autoren und Bücher
    UserBook.query.delete()
    BookList.query.delete()
    Book.query.delete()
    Author.query.delete()
    db.session.commit()
    print("Datenbank wurde geleert.")
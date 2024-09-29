from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc
from models import db, Author, Book, UserBook, BookList, User
import sys	

from app import create_app
from utils import fetch_google_books_info, get_author_image_from_wikimedia

app = create_app()
with app.app_context():
    # if python script command arg clean_db is set to True, the database will be cleaned before importing the data

    if '--clean_db' in sys.argv:
        UserBook.query.delete()
        BookList.query.delete()
        Book.query.delete()
        Author.query.delete()
        db.session.commit()
        print("Database has been cleared.")

    #setup new database if command arg
    if '--setup_db' in sys.argv:
        db.create_all()
        new_user = User(username="test", email="test@test.de", is_admin=True)
        new_user.set_password("test")
        db.session.add(new_user)
        db.session.commit()
        print("Database has been setup.")

    #if data cache file exists, load data from file
    try:
        with open('authors_books.txt', 'r', encoding="utf-8") as f:
            authors_books = {}
            for line in f:
                author, books = line.strip().split(': ')
                authors_books[author] = books[1:-1].split(', ')
    except FileNotFoundError:
        authors_books = {}

    if not authors_books:

        base_url = "https://thegreatestbooks.org/authors"
        pages_to_scrape = 10  # Anzahl der Seiten, die gescraped werden sollen

        options = Options()
        #options.add_argument('--headless')  # Optional: Webbrowser im Hintergrund ausführen
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Starte den WebDriver
        driver = uc.Chrome(options=options)


        for page in range(1, pages_to_scrape + 1):
            url = f"{base_url}/page/{page}"
            driver.get(url)

            time.sleep(2)  # Warte auf das Laden der Seite

            # Finde die Container für Autoren und deren Bücher
            authors = driver.find_elements(By.CLASS_NAME, 'mb-4')

            for author in authors:
                author_name = author.find_element(By.TAG_NAME, 'h3').find_element(
                    By.TAG_NAME, 'a').text.strip()  # Name des Autors
                books = author.find_elements(
                    By.CLASS_NAME, 'default-book-image')  # Container für Bücher

                # Füge den Autor und seine Bücher zur Liste hinzu
                author_books = []
                for book in books:
                    book_title = book.find_element(By.TAG_NAME, 'img').get_attribute(
                        'alt')  # Titel des Buches aus dem alt-Attribut
                    book_title = book_title.split(' by ')[0][10:-1]
                    author_books.append(book_title)

                authors_books[author_name] = author_books

        driver.quit()  # Schließe den WebDriver

        #cache data to file
        with open('authors_books.txt', 'w', encoding="utf-8") as f:
            for author, books in authors_books.items():
                f.write(f"{author}: {books}\n")

    # Ausgabe der gesammelten Daten
    for authorName, books in authors_books.items():

        # Finde den Autor oder erstelle ihn neu
        author = Author.query.filter_by(name=authorName).first()
        if not author:
            author = Author(name=authorName)
            db.session.add(author)

        for bookName in books:
            # Finde das Buch oder erstelle es neu
            book = Book.query.filter_by(title=bookName,
                                        author_id=author.id).first()
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

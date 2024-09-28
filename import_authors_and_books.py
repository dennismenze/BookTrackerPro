from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc
from models import db, Author, Book, UserBook, BookList
from flask import current_app

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

import re
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc
from models import db, Author, Book, UserBook, BookList, User, List
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
        List.query.delete()
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

        time.sleep(1)  # Warte auf das Laden der Seite

        # Finde die Container für Autoren und deren Bücher
        authors = driver.find_elements(By.CLASS_NAME, 'mb-4')
        driver.switch_to.new_window('tab')

        for author in authors:
            driver.switch_to.window(driver.window_handles[0])
            author_name = author.find_element(By.TAG_NAME, 'h3').find_element(
                By.TAG_NAME, 'a').text.strip()  # Name des Autors
            aut = Author(name=author_name)
            db.session.add(aut)
            db.session.commit()

            books = author.find_elements(
                By.CLASS_NAME, 'default-book-image')  # Container für Bücher

            # Füge den Autor und seine Bücher zur Liste hinzu
            
            for book in books:
                driver.switch_to.window(driver.window_handles[0])
                book_href = book.find_element(By.TAG_NAME, 'a').get_attribute('href')  # Link zum Buch
                book_title = book.find_element(By.TAG_NAME, 'img').get_attribute('alt')  # Titel des Buches aus dem alt-Attribut
                book_title = book_title.split(' by ')[0][10:-1]

                driver.switch_to.window(driver.window_handles[1])
                driver.get(book_href)
                time.sleep(1)
                listitems = driver.find_elements(By.CLASS_NAME, 'list-group-item')
                for listitem in listitems:
                    list_name = listitem.find_element(By.TAG_NAME, 'a').text
                    list_owner = listitem.text.split(' (')[1][:-1]
                    list_name = list_name + ' (' + list_owner + ')'
                    list_rank = listitem.text.split(' ')[0]
                    list_rank = re.sub(r'[^\d]', '', list_rank)
                    if list_rank == '':
                        list_rank = 0
                    else:
                        list_rank = int(list_rank)

                list = List.query.filter_by(name=list_name, user_id=1).first()
                if not list:
                    list = List(name=list_name, user_id=1)
                    db.session.add(list)
                    db.session.commit()

                r = driver.find_elements("tag name", "h3")
                i = 0
                for h3 in r:
                    rank = r[i].text
                    rank = rank.split(' ')[1]
                    rank = re.sub(r'[^\d]', '', rank)
                    if rank != '':
                        rank = int(rank)
                        break
                
                bk = Book(
                    title=book_title,
                    author=aut,
                    is_main_work=rank < 1000
                )
                db.session.add(bk)
                db.session.commit()

                book_list = BookList.query.filter_by(book_id=bk.id, list_id=list.id).first()	
                if not book_list:
                    book_list = BookList(book_id=bk.id, list_id=list.id)
                    book_list.rank = list_rank
                    db.session.add(book_list)
                    db.session.commit()          
                


    driver.quit()  # Schließe den WebDriver

    # Änderungen speichern
    db.session.commit()
    print("Daten wurden erfolgreich importiert.")

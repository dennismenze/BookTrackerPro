import re
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc
from models import db, Author, Book, UserBook, BookList, User, List, Translation
import sys

from flask import Flask
from utils import fetch_google_books_info, get_author_image_from_wikimedia
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Clear or set up the database
    if True: #'--clean_db' in sys.argv:
        UserBook.query.delete()
        BookList.query.delete()
        Book.query.delete()
        Author.query.delete()
        List.query.delete()
        Translation.query.delete()
        db.session.commit()
        print("Database has been cleared.")

    if '--setup_db' in sys.argv:
        db.create_all()
        new_user = User(username="test", email="test@test.de", is_admin=True)
        new_user.set_password("test")
        db.session.add(new_user)
        db.session.commit()
        print("Database has been set up.")

    # Define LibraryThing URL
    base_url = "https://www.librarything.com/"
    authors_page_url = f"{base_url}browse/authors"

    # Set up Chrome options
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Start the WebDriver
    driver = uc.Chrome(options=options)

    try:
        # Load the authors page
        driver.get(authors_page_url)

        # Wait for the authors list to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.authorName'))
        )

        # Find authors on the page
        author_elements = driver.find_elements(By.CSS_SELECTOR, '.authorName')
        driver.switch_to.new_window('tab')

        for author_element in author_elements:
            driver.switch_to.window(driver.window_handles[0])
            author_name = author_element.text.strip()
            author_href = author_element.get_attribute('href')

            # Check if author already exists in the database
            aut = Author.query.join(Translation, Author.name_id == Translation.id).filter(
                (Translation.text_en == author_name) | (Translation.text_de == author_name)
            ).first()
            if not aut:
                # Create translation entries for author name and bio
                name_translation = Translation(text_en=author_name, text_de=author_name)
                db.session.add(name_translation)
                db.session.flush()

                bio_translation = Translation(text_en="", text_de="")
                db.session.add(bio_translation)
                db.session.flush()

                aut = Author(name_id=name_translation.id, bio_id=bio_translation.id)
                db.session.add(aut)
                db.session.commit()

            # Visit author page for more details
            driver.switch_to.window(driver.window_handles[1])
            driver.get(author_href)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bookTitle')))

            # Extract and save author bio (if available)
            try:
                bio_element = driver.find_element(By.CSS_SELECTOR, '.authorBio')
                bio_translation.text_en = bio_element.text.strip()
                db.session.commit()
            except:
                pass  # No bio available

            # Extract the list of books for the author
            book_elements = driver.find_elements(By.CSS_SELECTOR, '.bookTitle')

            for book_element in book_elements:
                driver.switch_to.window(driver.window_handles[1])
                book_title = book_element.text.strip()
                book_href = book_element.get_attribute('href')

                # Check if the book is already in the database
                bk = Book.query.join(Translation, Book.title_id == Translation.id).filter(
                    (Translation.text_en == book_title) | (Translation.text_de == book_title),
                    Book.author_id == aut.id
                ).first()
                if not bk:
                    # Create translation entries for book title and description
                    title_translation = Translation(text_en=book_title, text_de=book_title)
                    db.session.add(title_translation)
                    db.session.flush()

                    description_translation = Translation(text_en="", text_de="")
                    db.session.add(description_translation)
                    db.session.flush()

                    # Create the Book entry
                    bk = Book(
                        title_id=title_translation.id,
                        description_id=description_translation.id,
                        author_id=aut.id,
                        is_main_work=False  # Set to False initially; can update later
                    )
                    db.session.add(bk)

                    # Visit the book page for additional details
                    driver.switch_to.new_window('tab')
                    driver.get(book_href)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bookDetails')))

                    # Extract book description if available
                    try:
                        description_element = driver.find_element(By.CSS_SELECTOR, '.bookDescription')
                        description_translation.text_en = description_element.text.strip()
                        db.session.commit()
                    except:
                        pass  # No description available

                    # Extract ranking information if available
                    try:
                        rank_element = driver.find_element(By.CSS_SELECTOR, '.bookRank')
                        rank = int(re.search(r'(\d+)', rank_element.text).group(1))
                        bk.is_main_work = rank < 1000
                        db.session.commit()
                    except:
                        pass  # No ranking available

                    # Close book tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[1])

                # Extract list information related to the book
                list_elements = driver.find_elements(By.CSS_SELECTOR, '.listGroupItem')
                for list_element in list_elements:
                    list_name = list_element.text.strip()

                    # Check if the list already exists in the database
                    list_obj = List.query.join(Translation, List.name_id == Translation.id).filter(
                        ((Translation.text_en == list_name) | (Translation.text_de == list_name)) &
                        (List.user_id == 1)
                    ).first()
                    if not list_obj:
                        # Create translation entries for list name and description
                        name_translation = Translation(text_en=list_name, text_de=list_name)
                        db.session.add(name_translation)
                        db.session.flush()

                        description_translation = Translation(text_en="", text_de="")
                        db.session.add(description_translation)
                        db.session.flush()

                        list_obj = List(name_id=name_translation.id, description_id=description_translation.id, user_id=1, is_public=True)
                        db.session.add(list_obj)
                        db.session.commit()

                    # Create relationship between Book and List
                    book_list = BookList.query.filter_by(book_id=bk.id, list_id=list_obj.id).first()
                    if not book_list:
                        book_list = BookList(book_id=bk.id, list_id=list_obj.id)
                        db.session.add(book_list)
                        db.session.commit()

                db.session.commit()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Quit the WebDriver
        driver.quit()
        # Commit any remaining changes to the database
        db.session.commit()
        print("Data has been successfully imported.")

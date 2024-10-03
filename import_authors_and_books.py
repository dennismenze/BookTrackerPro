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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = create_app()
with app.app_context():
    # If command arg '--clean_db' is provided, clear the database
    if True: #'--clean_db' in sys.argv:
        UserBook.query.delete()
        BookList.query.delete()
        Book.query.delete()
        Author.query.delete()
        List.query.delete()
        db.session.commit()
        print("Database has been cleared.")

    # If command arg '--setup_db' is provided, set up the new database
    if '--setup_db' in sys.argv:
        db.create_all()
        new_user = User(username="test", email="test@test.de", is_admin=True)
        new_user.set_password("test")
        db.session.add(new_user)
        db.session.commit()
        print("Database has been set up.")

    # Define base URL and number of pages to scrape
    base_url = "https://thegreatestbooks.org/authors"
    pages_to_scrape = 10  # Number of pages to be scraped

    # Set up Chrome options
    options = Options()
    # options.add_argument('--headless')  # Uncomment this for headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Start the WebDriver
    driver = uc.Chrome(options=options)

    try:
        for page in range(1, pages_to_scrape + 1):
            url = f"{base_url}/page/{page}"
            driver.get(url)

            # Wait for authors to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'mb-4'))
            )

            # Find containers for authors and their books
            authors = driver.find_elements(By.CLASS_NAME, 'mb-4')
            driver.switch_to.new_window('tab')

            for author in authors:
                driver.switch_to.window(driver.window_handles[0])
                author_name = author.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').text.strip()
                
                # Check if the author already exists in the database
                aut = Author.query.filter_by(name=author_name).first()
                if not aut:
                    aut = Author(name=author_name)
                    db.session.add(aut)
                    db.session.commit()

                books = author.find_elements(By.CLASS_NAME, 'default-book-image')

                # Iterate over books of the author
                for book in books:
                    driver.switch_to.window(driver.window_handles[0])
                    book_href = book.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    book_title = book.find_element(By.TAG_NAME, 'img').get_attribute('alt').split(' by ')[0][10:-1]

                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(book_href)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.list-group-item a')))

                    # Extract rank from the book's individual page
                    rank_elements = driver.find_elements(By.TAG_NAME, 'h3')
                    rank = 0
                    for element in rank_elements:
                        rank_text = element.text
                        rank_match = re.search(r'(\d+)', rank_text)
                        if rank_match:
                            rank = int(rank_match.group(1))
                            break

                    # Create Book object
                    bk = Book(
                        title=book_title,
                        author=aut,
                        is_main_work=(rank < 1000 if rank else False)
                    )
                    db.session.add(bk)

                    # Extract list information
                    listitems = driver.find_elements(By.CLASS_NAME, 'list-group-item')
                    for listitem in listitems:
                        listitem_text = listitem.text.strip()
                        count = 0
                        while not listitem_text and count < 10:
                            time.sleep(0.1)
                            listitem_text = listitem.text.strip()
                            count += 1
                        
                        if not listitem_text:
                            continue

                        # Extracting the rank number (if it exists)
                        list_rank_match = re.match(r'^(\d+)(?:st|nd|rd|th)', listitem_text)
                        list_rank = int(list_rank_match.group(1)) if list_rank_match else 0

                        # Extracting list name and owner
                        list_name_tag = listitem.find_element(By.TAG_NAME, 'a')
                        list_name = list_name_tag.text if list_name_tag else "Unknown List"

                        # Extract the last occurrence of text within parentheses for list_owner
                        list_owner_match = re.findall(r'\(([^)]+)\)', listitem_text)
                        list_owner = list_owner_match[-1] if list_owner_match else "Unknown Owner"

                        # Query or create the List in the database
                        list_obj = List.query.filter_by(name=list_name, user_id=1).first()
                        if not list_obj:
                            list_obj = List(name=list_name, user_id=1, is_public=True)
                            db.session.add(list_obj)
                            #db.session.commit()

                        
                        # Create relationship between Book and List
                        book_list = BookList.query.filter_by(book_id=bk.id, list_id=list_obj.id).first()
                        if not book_list:
                            book_list = BookList(book_id=bk.id, list_id=list_obj.id)
                            book_list.rank = list_rank
                            db.session.add(book_list)
                            #db.session.commit()

                db.session.commit()


    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Quit the WebDriver
        driver.quit()
        # Commit any remaining changes to the database
        db.session.commit()
        print("Data has been successfully imported.")

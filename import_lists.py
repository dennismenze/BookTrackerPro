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
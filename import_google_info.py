import time
from models import db, Author, Book, Translation
from utils import fetch_google_books_info, fetch_google_authors_info, get_author_image_from_wikimedia, search_german_title_bookbrainz
from flask import Flask
from config import Config  # Stellen Sie sicher, dass Sie eine config.py Datei haben

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def import_google_info(update_missing_only=True):
    with app.app_context():
        # Autoren aktualisieren
        authors = Author.query.all()
        total_authors = len(authors)
        for index, author in enumerate(authors, 1):
            author_name = Translation.query.get(author.name_id)
            bio_translation = Translation.query.get(author.bio_id)
            
            should_update = not update_missing_only or \
                            not author.image_url or \
                            not author_name.text_de or \
                            not bio_translation.text_en or \
                            not bio_translation.text_de

            if should_update:
                #author_info = fetch_google_authors_info(author_name.text_en)
                #if author_info:
                author.image_url = get_author_image_from_wikimedia(author_name.text_en)
                author_name.text_de = author_name.text_en
                    
                    #if bio_translation:
                        #bio_translation.text_en = author_info.get('biography_en') or bio_translation.text_en
                        #bio_translation.text_de = author_info.get('biography_de') or bio_translation.text_en
                    
                db.session.add(author)
                    #db.session.add(author_name)
                    #if bio_translation:
                        #db.session.add(bio_translation)
                
                if index % 50 == 0 or index == total_authors:
                    db.session.commit()
                    print(f"Autoren aktualisiert: {index}/{total_authors}")
                
                #time.sleep(0.7)
        
        # Bücher aktualisieren
        books = Book.query.all()
        total_books = len(books)
        for index, book in enumerate(books, 1):
            title_translation = Translation.query.get(book.title_id)
            description_translation = Translation.query.get(book.description_id)
            
            should_update = not update_missing_only or \
                            not book.isbn or \
                            not book.cover_image_url or \
                            not book.page_count or \
                            not book.published_date or \
                            not title_translation.text_de or \
                            not description_translation.text_en or \
                            not description_translation.text_de

            if should_update:
                author_name = Translation.query.get(book.author.name_id).text_en
                book_info = fetch_google_books_info(title_translation.text_en, author_name)
                if book_info:
                    book.isbn = book_info.get('isbn') or book.isbn
                    book.cover_image_url = book_info.get('cover_image_url') or book.cover_image_url
                    book.page_count = book_info.get('page_count') or book.page_count
                    book.published_date = book_info.get('published_date') or book.published_date
                    
                    title_translation.text_de = search_german_title_bookbrainz(title_translation.text_en) or title_translation.text_de
                    
                    if description_translation:
                        description_translation.text_en = book_info.get('description_en') or description_translation.text_en
                        description_translation.text_de = book_info.get('description_de') or description_translation.text_de
                    
                    db.session.add(book)
                    db.session.add(title_translation)
                    if description_translation:
                        db.session.add(description_translation)
                
                if index % 50 == 0 or index == total_books:
                    db.session.commit()
                    print(f"Bücher aktualisiert: {index}/{total_books}")
                
                time.sleep(0.7)
        
        print("Google-Informationen wurden erfolgreich importiert.")

if __name__ == "__main__":
    import sys
    update_missing_only = True
    if len(sys.argv) > 1 and sys.argv[1] == "--update-all":
        update_missing_only = False
    import_google_info(update_missing_only)
import time
from models import db, Author, Book, Translation
from utils import search_german_title_wikidata, search_german_author_name_wikidata
from flask import Flask
from config import Config  # Stellen Sie sicher, dass Sie eine config.py Datei haben

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def import_google_info(update_missing_only=True):
    with app.app_context(): 

        # # Autoren aktualisieren
        # authors = Author.query.all()
        # total_authors = len(authors)
        # print(total_authors)
        # for index, author in enumerate(authors, 1):
        #     author_translation = Translation.query.get(author.name_id)
        #     author_translation.text_de = search_german_author_name_wikidata(author_translation.text_en) or author_translation.text_en
        #     print(author_translation.text_en, author_translation.text_de)
        #     db.session.add(author_translation)

        #     if index % 50 == 0 or index == total_authors:
        #         db.session.commit()
        #         print(f"Autoren aktualisiert: {index}/{total_authors}")
                
        #     time.sleep(0.6)

        

        # Bücher aktualisieren
        books = Book.query.all()
        total_books = len(books)
        print(total_books)
        for index, book in enumerate(books, 1):
            title_translation = Translation.query.get(book.title_id)
            
            should_update = not update_missing_only or \
                            not title_translation.text_de

            if should_update:
                author_name = Translation.query.get(book.author.name_id).text_en
                title_translation.text_de = search_german_title_wikidata(author_name, title_translation.text_en) or title_translation.text_en
                print(title_translation.text_en, title_translation.text_de)
                db.session.add(title_translation)
                
                if index % 50 == 0 or index == total_books:
                    db.session.commit()
                    print(f"Bücher aktualisiert: {index}/{total_books}")
                
                time.sleep(0.6)
        
        print("Deutsche Titel wurden erfolgreich importiert.")

if __name__ == "__main__":
    import sys
    update_missing_only = True
    if len(sys.argv) > 1 and sys.argv[1] == "--update-all":
        update_missing_only = False
    import_google_info(update_missing_only)
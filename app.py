import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging
from urllib.parse import urlparse
from models import init_models

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    app.logger.info(f"Raw DATABASE_URL: {database_url}")
    
    if database_url:
        try:
            parsed_url = urlparse(database_url)
            app.logger.info(f"Parsed URL: scheme={parsed_url.scheme}, hostname={parsed_url.hostname}, port={parsed_url.port}, path={parsed_url.path}")
            
            # Ensure the port is a valid integer
            port = parsed_url.port if parsed_url.port else 5432  # Default PostgreSQL port
            
            database_url = f'{parsed_url.scheme}://{parsed_url.hostname}:{port}{parsed_url.path}'
            app.logger.info(f"Formatted DATABASE_URL: {database_url}")
        except Exception as e:
            app.logger.error(f"Error parsing DATABASE_URL: {str(e)}")
            database_url = None
    else:
        app.logger.error("DATABASE_URL environment variable is not set")

    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    else:
        app.logger.error("Unable to configure database. The application may not function correctly.")

    db.init_app(app)
    
    with app.app_context():
        try:
            app.logger.info("Initializing database...")
            Book, Author, List, book_list = init_models(db)
            db.create_all()
            app.logger.info("Database tables created successfully")

            app.logger.info("Registering blueprints...")
            from routes import book_routes, author_routes, list_routes
            app.register_blueprint(book_routes.bp)
            app.register_blueprint(author_routes.bp)
            app.register_blueprint(list_routes.bp)
            app.logger.info("Blueprints registered successfully")

            app.logger.info("Adding sample data...")
            add_sample_data(Book, Author, List)
            app.logger.info("Sample data added successfully")
        except Exception as e:
            app.logger.error(f"Error during app initialization: {str(e)}")
            # Don't raise the exception here, as we want the app to start even if there are issues

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/authors')
    def authors():
        return render_template('author/list.html')

    @app.route('/lists')
    def lists():
        return render_template('list/list.html')

    @app.route('/author/<int:id>')
    def author_detail(id):
        return render_template('author/detail.html')

    @app.route('/list/<int:id>')
    def list_detail(id):
        return render_template('list/detail.html')

    return app

def add_sample_data(Book, Author, List):
    # Check if data already exists
    if Author.query.first() is not None:
        return  # Data already exists, no need to add sample data

    # Create authors
    author1 = Author(name='Jane Austen')
    author2 = Author(name='George Orwell')
    db.session.add_all([author1, author2])
    db.session.commit()

    # Create books
    book1 = Book(title='Pride and Prejudice', author=author1, is_read=True)
    book2 = Book(title='1984', author=author2, is_read=False)
    db.session.add_all([book1, book2])
    db.session.commit()

    # Create lists
    list1 = List(name='Classics')
    list1.books.extend([book1, book2])
    db.session.add(list1)
    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    app.logger.info("Starting Flask application")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

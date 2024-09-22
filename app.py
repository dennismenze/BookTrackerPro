import os
from flask import Flask, render_template
from models import db, Book, Author, List
import logging

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy
    db.init_app(app)

    app.logger.debug(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Create tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise

    # Register blueprints
    from routes import book_routes, author_routes, list_routes
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(author_routes.bp)
    app.register_blueprint(list_routes.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/authors')
    def authors():
        return render_template('author/list.html')

    @app.route('/author/<int:id>')
    def author_detail(id):
        return render_template('author/detail.html', author_id=id)

    @app.route('/book/<int:id>')
    def book_detail(id):
        return render_template('book/detail.html', book_id=id)

    @app.route('/lists')
    def lists():
        return render_template('list/list.html')

    @app.route('/list/<int:id>')
    def list_detail(id):
        return render_template('list/detail.html', list_id=id)

    @app.route('/db-info')
    def db_info():
        return f'Database connection: {app.config["SQLALCHEMY_DATABASE_URI"]}'

    return app

def add_sample_data(app):
    with app.app_context():
        # Check if the database is empty
        if Book.query.count() == 0:
            try:
                # Add sample authors
                author1 = Author(name="J.K. Rowling")
                author2 = Author(name="George Orwell")
                author3 = Author(name="Jane Austen")
                db.session.add_all([author1, author2, author3])
                db.session.commit()

                # Add sample books
                book1 = Book(title="Harry Potter and the Philosopher's Stone", author=author1, is_read=True)
                book2 = Book(title="1984", author=author2, is_read=False)
                book3 = Book(title="Pride and Prejudice", author=author3, is_read=True)
                db.session.add_all([book1, book2, book3])
                db.session.commit()

                app.logger.info("Sample data added successfully")
            except Exception as e:
                app.logger.error(f"Error adding sample data: {str(e)}")
                db.session.rollback()

if __name__ == '__main__':
    app = create_app()
    add_sample_data(app)
    app.run(host='0.0.0.0', port=5000, debug=True)

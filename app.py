import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging
from urllib.parse import urlparse

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
    if not database_url:
        app.logger.error("DATABASE_URL is not set in the environment variables.")
        raise ValueError("DATABASE_URL is not set")
    
    # Parse the database URL to remove sensitive information
    parsed_url = urlparse(database_url)
    safe_db_url = f"{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}/{parsed_url.path}"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.logger.info(f"Database connection: {safe_db_url}")
    
    db.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise

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

    @app.route('/lists')
    def lists():
        return render_template('list/list.html')

    @app.route('/db-info')
    def db_info():
        return f'Database connection: {safe_db_url}'

    return app

if __name__ == '__main__':
    try:
        app = create_app()
        app.logger.info("Starting Flask application")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logging.error(f"Failed to start the application: {str(e)}")

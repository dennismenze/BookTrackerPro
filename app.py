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

    # Parse the database URL
    parsed_url = urlparse(database_url)
    username = parsed_url.username
    password = parsed_url.password
    hostname = parsed_url.hostname
    port = parsed_url.port or 5432  # Use default PostgreSQL port if not specified
    database = parsed_url.path[1:]  # Remove the leading '/'

    # Construct the SQLAlchemy database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Log a safe version of the database URL (without credentials)
    safe_db_url = f"postgresql://{hostname}:{port}/{database}"
    app.logger.info(f"Database connection: {safe_db_url}")
    
    # Initialize SQLAlchemy
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

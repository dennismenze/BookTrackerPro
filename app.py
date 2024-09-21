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
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        app.logger.error("DATABASE_URL environment variable is not set")
        raise ValueError("DATABASE_URL must be set")
    
    # Log the database URL (without exposing sensitive information)
    parsed_url = urlparse(app.config["SQLALCHEMY_DATABASE_URI"])
    app.logger.info(f"Using database: {parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}{parsed_url.path}")
    
    db.init_app(app)
    
    try:
        from routes import book_routes, author_routes, list_routes
        app.register_blueprint(book_routes.bp)
        app.register_blueprint(author_routes.bp)
        app.register_blueprint(list_routes.bp)
        app.logger.info("Blueprints registered successfully")
    except Exception as e:
        app.logger.error(f"Error registering blueprints: {str(e)}")
        raise

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

    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise

    return app

if __name__ == "__main__":
    app = create_app()
    app.logger.info("Starting Flask application")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

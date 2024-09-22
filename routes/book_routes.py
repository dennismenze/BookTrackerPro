from flask import Blueprint, jsonify, request, current_app
from app import db
from models import Book, Author, List
import logging

bp = Blueprint('book', __name__, url_prefix='/api/books')

@bp.route('/', methods=['GET'])
def get_books():
    try:
        current_app.logger.debug(f"Database URI: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
        books = Book.query.all()
        return jsonify([{
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'is_read': book.is_read
        } for book in books])
    except Exception as e:
        current_app.logger.error(f"Error in get_books: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching books'}), 500

# Rest of the file remains the same

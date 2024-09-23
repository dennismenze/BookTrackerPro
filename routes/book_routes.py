from flask import Blueprint, jsonify, request, current_app, session, abort
from flask_login import login_required, current_user
from models import db, Book, Author, List
from sqlalchemy import or_
import requests

bp = Blueprint('book', __name__, url_prefix='/api/books')

@bp.before_request
def check_auth():
    current_app.logger.debug(f"check_auth called. Session: {session}")
    current_app.logger.debug(f"current_user.is_authenticated: {current_user.is_authenticated}")
    if not current_user.is_authenticated:
        current_app.logger.warning(f"User not authenticated. Session: {session}")
        abort(401)  # Unauthorized
    else:
        current_app.logger.debug(f"User authenticated. User ID: {current_user.id}")

@bp.route('/', methods=['GET'])
@login_required
def get_books():
    try:
        current_app.logger.debug(f"Database URI: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
        search_query = request.args.get('search', '')
        if search_query:
            books = Book.query.join(Author).filter(
                Book.users.any(id=current_user.id),
                or_(
                    Book.title.ilike(f'%{search_query}%'),
                    Author.name.ilike(f'%{search_query}%')
                )
            ).all()
        else:
            books = Book.query.filter(Book.users.any(id=current_user.id)).all()
        return jsonify([{
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'is_read': book.is_read,
            'cover_image_url': book.cover_image_url
        } for book in books])
    except Exception as e:
        current_app.logger.error(f"Error in get_books: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching books'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_book(id):
    book = Book.query.filter(Book.id == id, Book.users.any(id=current_user.id)).first_or_404()
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'author_id': book.author_id,
        'is_read': book.is_read,
        'isbn': book.isbn,
        'description': book.description,
        'cover_image_url': book.cover_image_url,
        'page_count': book.page_count,
        'published_date': book.published_date,
        'lists': [{'id': list.id, 'name': list.name} for list in book.lists if list.user_id == current_user.id]
    })

@bp.route('/', methods=['POST'])
@login_required
def create_book():
    data = request.get_json()
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    author = Author.query.filter_by(name=data['author']).first()
    if not author:
        author = Author(name=data['author'])
        db.session.add(author)

    existing_book = Book.query.filter(Book.title == data['title'], Book.author == author, Book.users.any(id=current_user.id)).first()
    if existing_book:
        return jsonify({
            'id': existing_book.id,
            'message': 'Book already exists'
        }), 200

    # Fetch book information from Google Books API
    google_books_info = fetch_google_books_info(data['title'], data['author'])

    book = Book(
        title=data['title'],
        author=author,
        isbn=google_books_info.get('isbn'),
        description=google_books_info.get('description'),
        cover_image_url=google_books_info.get('cover_image_url'),
        page_count=google_books_info.get('page_count'),
        published_date=google_books_info.get('published_date')
    )
    book.users.append(current_user)
    db.session.add(book)
    db.session.commit()

    return jsonify({
        'id': book.id,
        'message': 'Book created successfully'
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_book(id):
    book = Book.query.filter(Book.id == id, Book.users.any(id=current_user.id)).first_or_404()
    data = request.get_json()
    if data and 'title' in data:
        book.title = data['title']
    if data and 'is_read' in data:
        book.is_read = data['is_read']
    db.session.commit()
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'is_read': book.is_read,
        'message': 'Book updated successfully'
    })

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_book(id):
    book = Book.query.filter(Book.id == id, Book.users.any(id=current_user.id)).first_or_404()
    current_user.books.remove(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

def fetch_google_books_info(title, author):
    try:
        query = f"{title} {author}".replace(" ", "+")
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}")
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            book_info = data['items'][0]['volumeInfo']
            return {
                'isbn': book_info.get('industryIdentifiers', [{}])[0].get('identifier', ''),
                'description': book_info.get('description', ''),
                'cover_image_url': book_info.get('imageLinks', {}).get('thumbnail', ''),
                'page_count': book_info.get('pageCount', 0),
                'published_date': book_info.get('publishedDate', '')
            }
        return {}
    except Exception as e:
        current_app.logger.error(f"Error fetching Google Books info: {str(e)}")
        return {}

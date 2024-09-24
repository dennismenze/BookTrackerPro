from flask import Blueprint, jsonify, request, current_app, session, abort
from flask_login import login_required, current_user
from models import db, Book, Author, List, UserBook
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
        
        # Query for books that the user has marked as read
        books_query = Book.query.join(UserBook).filter(
            UserBook.user_id == current_user.id,
            UserBook.is_read == True
        )
        
        if search_query:
            books_query = books_query.join(Author).filter(
                or_(
                    Book.title.ilike(f'%{search_query}%'),
                    Author.name.ilike(f'%{search_query}%')
                )
            )
        
        books = books_query.all()
        
        return jsonify([{
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'cover_image_url': book.cover_image_url
        } for book in books])
    except Exception as e:
        current_app.logger.error(f"Error in get_books: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching books'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_book(id):
    try:
        current_app.logger.info(f"Fetching book with id: {id}")
        book = Book.query.get_or_404(id)
        
        current_app.logger.info(f"Book found: {book.title}")
        
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
        
        user_lists = [list for list in book.lists if list.user_id == current_user.id]
        
        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'author_id': book.author_id,
            'is_read': user_book.is_read if user_book else False,
            'isbn': book.isbn,
            'description': book.description,
            'cover_image_url': book.cover_image_url,
            'page_count': book.page_count,
            'published_date': book.published_date,
            'lists': [{'id': list.id, 'name': list.name} for list in user_lists],
            'in_user_collection': user_book is not None
        }
        
        current_app.logger.debug(f"Returning book data: {book_data}")
        return jsonify(book_data)
    except Exception as e:
        current_app.logger.error(f"Error in get_book: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching the book'}), 500

@bp.route('/', methods=['POST'])
@login_required
def create_book():
    data = request.get_json()
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    existing_book = Book.query.filter(
        Book.title == data['title'],
        Book.author.has(name=data['author']),
        Book.users.any(id=current_user.id)
    ).first()

    if existing_book:
        return jsonify({
            'id': existing_book.id,
            'message': 'Book already exists for this user'
        }), 200

    author = Author.query.filter_by(name=data['author']).first()
    if not author:
        author = Author(name=data['author'])
        db.session.add(author)

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
    try:
        current_app.logger.info(f"Updating book with id: {id}")
        book = Book.query.get_or_404(id)
        current_app.logger.info(f"Book found: {book.title}")

        data = request.get_json()
        current_app.logger.debug(f"Received data: {data}")

        if data and 'title' in data:
            book.title = data['title']
        
        if data and 'is_read' in data:
            user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=id).first()
            if user_book:
                user_book.is_read = data['is_read']
            else:
                new_user_book = UserBook(user_id=current_user.id, book_id=id, is_read=data['is_read'])
                db.session.add(new_user_book)

        db.session.commit()
        current_app.logger.info(f"Book updated successfully: {book.title}")

        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'is_read': data.get('is_read', False),
            'message': 'Book updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating book: {str(e)}")
        return jsonify({'error': 'An error occurred while updating the book'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_book(id):
    book = Book.query.filter(Book.id == id, Book.users.any(id=current_user.id)).first_or_404()
    current_user.books.remove(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

@bp.route('/<int:id>/read_status', methods=['PUT'])
@login_required
def update_read_status(id):
    try:
        current_app.logger.info(f"Updating read status for book {id}")
        data = request.get_json()
        is_read = data.get('is_read', False)
        current_app.logger.info(f"New read status: {is_read}")
        
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=id).first()
        if user_book:
            current_app.logger.info(f"Existing user_book found, updating status")
            user_book.is_read = is_read
        else:
            current_app.logger.info(f"No existing user_book found, creating new entry")
            book = Book.query.get_or_404(id)
            new_user_book = UserBook(user_id=current_user.id, book_id=id, is_read=is_read)
            db.session.add(new_user_book)
        
        db.session.commit()
        current_app.logger.info(f"Read status updated successfully")
        return jsonify({'message': 'Read status updated successfully', 'is_read': is_read})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating read status: {str(e)}")
        return jsonify({'error': 'An error occurred while updating the read status'}), 500

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
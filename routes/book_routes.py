from flask import Blueprint, jsonify, request, current_app, abort
from flask_login import login_required, current_user
from models import db, Book, Author, List, UserBook
from sqlalchemy import func, or_
import requests

bp = Blueprint('book', __name__, url_prefix='/api/books')

@bp.before_request
def check_auth():
    if not current_user.is_authenticated:
        abort(401)  # Unauthorized

@bp.route('/', methods=['GET'])
@login_required
def get_books():
    try:
        search_query = request.args.get('search', '')

        books_query = Book.query.join(UserBook).filter(
            UserBook.user_id == current_user.id, UserBook.is_read == True)

        if search_query:
            books_query = books_query.join(Author).filter(
                or_(Book.title.ilike(f'%{search_query}%'),
                    Author.name.ilike(f'%{search_query}%')))

        books = books_query.all()

        return jsonify([{
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'cover_image_url': book.cover_image_url
        } for book in books])
    except Exception as e:
        current_app.logger.error(f"Error in get_books: {str(e)}")
        return jsonify({'error':
                        'An error occurred while fetching books'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_book(id):
    try:
        current_app.logger.info(f"Fetching book with id: {id}")
        book = Book.query.get_or_404(id)

        current_app.logger.info(f"Book found: {book.title}")

        user_book = UserBook.query.filter_by(user_id=current_user.id,
                                             book_id=book.id).first()

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
            'lists': [],
            'in_user_collection': user_book is not None,
            'is_main_work': book.is_main_work
        }

        try:
            if hasattr(book, 'lists'):
                book_data['lists'] = [{
                    'id': list.id,
                    'name': list.name
                } for list in book.lists if list.user_id == current_user.id or list.user_id is None]
                current_app.logger.debug(f"Book {id} lists: {book_data['lists']}")
            else:
                current_app.logger.warning(f"Book {id} does not have 'lists' attribute")
        except Exception as e:
            current_app.logger.error(f"Error processing lists for book {id}: {str(e)}")

        if not all([book.isbn, book.description, book.cover_image_url, book.page_count, book.published_date]):
            current_app.logger.info(f"Fetching missing information for book {id} from Google Books API")
            google_books_info = fetch_google_books_info(book.title, book.author.name)
            
            book_data['isbn'] = book.isbn or google_books_info.get('isbn')
            book_data['description'] = book.description or google_books_info.get('description')
            book_data['cover_image_url'] = book.cover_image_url or google_books_info.get('cover_image_url')
            book_data['page_count'] = book.page_count or google_books_info.get('page_count')
            book_data['published_date'] = book.published_date or google_books_info.get('published_date')

            book.isbn = book_data['isbn']
            book.description = book_data['description']
            book.cover_image_url = book_data['cover_image_url']
            book.page_count = book_data['page_count']
            book.published_date = book_data['published_date']
            
            db.session.commit()
            current_app.logger.info(f"Updated book {id} with Google Books API information")

        current_app.logger.debug(f"Returning book data: {book_data}")
        return jsonify(book_data)
    except Exception as e:
        current_app.logger.error(f"Error in get_book: {str(e)}")
        return jsonify({'error':
                        'An error occurred while fetching the book'}), 500

@bp.route('/<int:id>/read_status', methods=['PUT'])
@login_required
def update_read_status(id):
    try:
        current_app.logger.info(f"Updating read status for book {id}")
        book = Book.query.get_or_404(id)
        data = request.get_json()
        is_read = data.get('is_read', False)

        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=id).first()
        if user_book:
            user_book.is_read = is_read
        else:
            new_user_book = UserBook(user_id=current_user.id, book_id=id, is_read=is_read)
            db.session.add(new_user_book)

        db.session.commit()
        current_app.logger.info(f"Read status updated successfully for book {id}")
        return jsonify({'message': 'Read status updated successfully', 'is_read': is_read})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating read status: {str(e)}")
        return jsonify({'error': 'An error occurred while updating the read status'}), 500

@bp.route('/<int:id>/toggle_main_work', methods=['PUT'])
@login_required
def toggle_main_work(id):
    try:
        current_app.logger.info(f"Toggling main work status for book {id}")
        book = Book.query.get_or_404(id)
        
        if not current_user.is_admin:
            current_app.logger.warning(f"Non-admin user {current_user.id} attempted to toggle main work status")
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403

        book.is_main_work = not book.is_main_work
        db.session.commit()
        current_app.logger.info(f"Main work status updated successfully for book {id}")
        return jsonify({'message': 'Main work status updated successfully', 'is_main_work': book.is_main_work})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating main work status: {str(e)}")
        return jsonify({'error': 'An error occurred while updating the main work status'}), 500

def fetch_google_books_info(title, author):
    try:
        query = f"intitle:{title}+inauthor:{author}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(url)
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            volume_info = data['items'][0]['volumeInfo']
            return {
                'isbn': volume_info.get('industryIdentifiers', [{}])[0].get('identifier'),
                'description': volume_info.get('description'),
                'cover_image_url': volume_info.get('imageLinks', {}).get('thumbnail'),
                'page_count': volume_info.get('pageCount'),
                'published_date': volume_info.get('publishedDate')
            }
        else:
            return {}
    except Exception as e:
        current_app.logger.error(f"Error fetching Google Books info: {str(e)}")
        return {}

from flask import Blueprint, jsonify, request, current_app, abort
from flask_login import login_required, current_user
from models import db, Author, Book, UserBook
from sqlalchemy import func, or_
from utils import calculate_read_percentage, calculate_read_main_works_percentage, map_author_data, map_book_data, get_books_stats

bp = Blueprint('author', __name__, url_prefix='/api/authors')

@bp.before_request
def check_auth():
    if not current_user.is_authenticated:
        abort(401)  # Unauthorized

@bp.route('/', methods=['GET'])
@login_required
def get_authors():
    try:
        search_query = request.args.get('search', '')
        
        user_authors_query = db.session.query(Author).join(Book).join(UserBook).filter(
            UserBook.user_id == current_user.id,
            UserBook.is_read == True
        ).distinct()
        
        all_authors_query = Author.query
        
        if search_query:
            user_authors_query = user_authors_query.filter(func.lower(Author.name).contains(func.lower(search_query)))
            all_authors_query = all_authors_query.filter(func.lower(Author.name).contains(func.lower(search_query)))
        
        user_authors = user_authors_query.all()
        all_authors = all_authors_query.all()
           
        result = {
            'all_authors': [{
                'id': author.id,
                'name': author.name,
                'book_count': len(author.books),
                'main_works_count': sum(1 for book in author.books if book.is_main_work),
                'read_main_works_percentage': calculate_read_main_works_percentage(author.books, current_user.id)
            } for author in all_authors],
            'user_authors': [{
                'id': author.id,
                'name': author.name,
                'book_count': sum(1 for book in author.books if any(user_book.user_id == current_user.id and user_book.is_read for user_book in book.user_books)),
                'read_percentage': calculate_read_percentage(author.books, current_user.id),
                'main_works_count': sum(1 for book in author.books if book.is_main_work),
                'read_main_works_percentage': calculate_read_main_works_percentage(author.books, current_user.id)
            } for author in user_authors]
        }

        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in get_authors: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching authors'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_author(id):
    author = Author.query.get_or_404(id)    
    author_data = map_author_data(author, current_user.id) 
    
    return jsonify(author_data)

@bp.route('/', methods=['POST'])
@login_required
def create_author():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    author = Author(name=data['name'])
    db.session.add(author)
    db.session.commit()
    return jsonify({
        'id': author.id,
        'message': 'Author created successfully'
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_author(id):
    author = Author.query.get_or_404(id)
    data = request.get_json()
    if data and 'name' in data:
        author.name = data['name']
    db.session.commit()
    return jsonify({'message': 'Author updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_author(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
    
    author = Author.query.get_or_404(id)
    try:
        db.session.delete(author)
        db.session.commit()
        return jsonify({'message': 'Author deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting author: {str(e)}")
        return jsonify({'error': 'An error occurred while deleting the author'}), 500

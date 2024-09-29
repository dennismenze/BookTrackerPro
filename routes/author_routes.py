from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Author, Book, UserBook
from sqlalchemy import func

bp = Blueprint('author', __name__)

@bp.route('/authors')
@login_required
def authors():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of authors per page
    search_query = request.args.get('search', '')

    query = Author.query

    if search_query:
        query = query.filter(Author.name.ilike(f'%{search_query}%'))

    authors = query.order_by(Author.name).paginate(page=page,
                                                   per_page=per_page,
                                                   error_out=False)

    return render_template('authors.html',
                           authors=authors,
                           search_query=search_query)

@bp.route('/<int:id>')
@login_required
def author_detail(id):
    author = Author.query.get_or_404(id)
    books = Book.query.filter_by(author_id=author.id).all()
    
    # Calculate statistics
    total_books = len(books)
    read_books = UserBook.query.filter(UserBook.book_id.in_([book.id for book in books]), 
                                       UserBook.user_id == current_user.id, 
                                       UserBook.is_read == True).count()
    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0
    
    return render_template('author_detail.html', 
                           author=author, 
                           books=books, 
                           total_books=total_books, 
                           read_books=read_books, 
                           read_percentage=read_percentage)

@bp.route('/author/authors')
def api_authors():
    search_query = request.args.get('search', '')
    authors = Author.query.filter(Author.name.ilike(f'%{search_query}%')).all()
    return jsonify([{
        'id': author.id,
        'name': author.name,
        'image_url': author.image_url
    } for author in authors])

# Remove the api_author_detail route as it's no longer needed

# Add other author-related routes here

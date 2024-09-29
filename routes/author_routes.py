from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Author, Book
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

    authors = query.order_by(Author.name).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('authors.html', authors=authors, search_query=search_query)

@bp.route('/<int:id>')
@login_required
def author_detail(id):
    return render_template('author/detail.html', author_id=id)

@bp.route('/api/authors')
def api_authors():
    search_query = request.args.get('search', '')
    authors = Author.query.filter(Author.name.ilike(f'%{search_query}%')).all()
    return jsonify([{'id': author.id, 'name': author.name, 'image_url': author.image_url} for author in authors])

@bp.route('/api/author/<int:id>')
@login_required
def api_author_detail(id):
    author = Author.query.get_or_404(id)
    books = Book.query.filter_by(author_id=author.id).all()
    return jsonify({
        'id': author.id,
        'name': author.name,
        'image_url': author.image_url,
        'books': [{
            'id': book.id,
            'title': book.title,
            'cover_image_url': book.cover_image_url
        } for book in books]
    })

# Add other author-related routes here

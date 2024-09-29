from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Author

bp = Blueprint('author', __name__)

@bp.route('/authors')
@login_required
def authors():
    return render_template('authors.html')

@bp.route('/<int:id>')
@login_required
def author_detail(id):
    return render_template('author/detail.html', author_id=id)

@bp.route('/api/authors')
def api_authors():
    print("API authors route hit")  # Debug print statement
    search_query = request.args.get('search', '')
    authors = Author.query.filter(Author.name.ilike(f'%{search_query}%')).all()
    print(f"Number of authors: {len(authors)}")  # Debug print statement
    return jsonify([{'id': author.id, 'name': author.name, 'image_url': author.image_url} for author in authors])

# Add other author-related routes here

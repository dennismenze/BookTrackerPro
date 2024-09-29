from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, List, Book, UserBook
from sqlalchemy.orm import joinedload

bp = Blueprint('list', __name__)

@bp.route('/lists')
@login_required
def lists():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')

    query = List.query.filter(List.user_id == current_user.id)

    if search_query:
        query = query.filter(List.name.ilike(f'%{search_query}%'))

    lists = query.order_by(List.name).paginate(page=page, per_page=per_page, error_out=False)

    # Fetch the first 5 books for each list
    for list_item in lists.items:
        list_item.preview_books = list_item.books[:5]
        list_item.book_count = len(list_item.books)

    return render_template('list/lists.html', lists=lists, search_query=search_query)

@bp.route('/list/<int:id>')
@login_required
def list_detail(id):
    book_list = List.query.get_or_404(id)
    
    # Ensure the user has permission to view this list
    if book_list.user_id != current_user.id and not book_list.is_public:
        flash('You do not have permission to view this list.', 'error')
        return redirect(url_for('list.lists'))
    
    # Fetch all books in the list with their read status
    books = []
    for book in book_list.books:
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
        books.append({
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'cover_image_url': book.cover_image_url,
            'is_read': user_book.is_read if user_book else False
        })
    
    return render_template('list/detail.html', list=book_list, books=books)

# Add other list-related routes here

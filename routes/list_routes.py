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
    total_books = len(book_list.books)
    read_books = 0
    for book in book_list.books:
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
        is_read = user_book.is_read if user_book else False
        if is_read:
            read_books += 1
        books.append({
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'cover_image_url': book.cover_image_url,
            'is_read': is_read
        })
    
    # Calculate the percentage of books read
    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0
    
    return render_template('list/detail.html', list=book_list, books=books, read_percentage=read_percentage)

@bp.route('/toggle_read_status', methods=['POST'])
@login_required
def toggle_read_status():
    data = request.json
    book_id = data.get('book_id')
    list_id = data.get('list_id')
    is_read = data.get('is_read')

    if book_id is None or list_id is None or is_read is None:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if user_book:
        user_book.is_read = is_read
    else:
        user_book = UserBook(user_id=current_user.id, book_id=book_id, is_read=is_read)
        db.session.add(user_book)

    db.session.commit()

    # Recalculate the read percentage
    book_list = List.query.get(list_id)
    total_books = len(book_list.books)
    read_books = UserBook.query.filter(UserBook.user_id == current_user.id, 
                                       UserBook.book_id.in_([book.id for book in book_list.books]), 
                                       UserBook.is_read == True).count()
    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0

    return jsonify({
        'success': True,
        'is_read': is_read,
        'read_percentage': round(read_percentage, 1)
    })

# Add other list-related routes here

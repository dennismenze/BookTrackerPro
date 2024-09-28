
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import db, Author, Book, UserBook
from sqlalchemy import func

bp = Blueprint('author', __name__)

@bp.route('/author/<int:id>')
@login_required
def author_detail(id):
    author = Author.query.get_or_404(id)
    total_books = Book.query.filter_by(author_id=author.id).count()
    total_pages = db.session.query(func.sum(Book.page_count)).filter(Book.author_id == author.id).scalar() or 0
    avg_pages = total_pages / total_books if total_books > 0 else 0
    books_read = UserBook.query.join(Book).filter(Book.author_id == author.id, UserBook.user_id == current_user.id, UserBook.is_read == True).count()
    books_reading = UserBook.query.join(Book).filter(Book.author_id == author.id, UserBook.user_id == current_user.id, UserBook.is_read == False).count()
    
    # Fetch books with their read status and is_main_work attribute
    books = db.session.query(Book, UserBook.is_read).outerjoin(UserBook, (UserBook.book_id == Book.id) & (UserBook.user_id == current_user.id)).filter(Book.author_id == author.id).all()
    
    # Prepare books data with read status and is_main_work attribute
    books_data = []
    for book, is_read in books:
        book_data = book.__dict__
        book_data['is_read'] = is_read if is_read is not None else False
        book_data['is_main_work'] = book.is_main_work  # Include is_main_work attribute
        books_data.append(book_data)
    
    return render_template('author/detail.html', 
                           author=author, 
                           total_books=total_books, 
                           total_pages=total_pages, 
                           avg_pages=avg_pages,
                           books_read=books_read,
                           books_reading=books_reading,
                           books=books_data)

@bp.route('/toggle_read_status/<int:book_id>', methods=['POST'])
@login_required
def toggle_read_status(book_id):
    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if user_book:
        user_book.is_read = not user_book.is_read
    else:
        user_book = UserBook(user_id=current_user.id, book_id=book_id, is_read=True)
        db.session.add(user_book)
    db.session.commit()
    return jsonify({'is_read': user_book.is_read})

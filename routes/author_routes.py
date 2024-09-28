from flask import Blueprint, render_template
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
    
    return render_template('author/detail.html', 
                           author=author, 
                           total_books=total_books, 
                           total_pages=total_pages, 
                           avg_pages=avg_pages,
                           books_read=books_read,
                           books_reading=books_reading)

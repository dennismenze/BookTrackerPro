from flask import Blueprint, render_template, request, redirect, url_for, flash, g, send_file
from flask_login import login_required, current_user, logout_user
from models import db, User, Book, Author, List, UserBook, Post
from sqlalchemy import func, desc
from io import BytesIO
from datetime import datetime, date

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    book_search_query = request.args.get('book_search', '')
    author_search_query = request.args.get('author_search', '')
    book_page = request.args.get('book_page', 1, type=int)
    author_page = request.args.get('author_page', 1, type=int)
    per_page = 10

    # Book search
    book_query = Book.query
    if book_search_query:
        book_query = book_query.filter(Book.title.ilike(f'%{book_search_query}%'))
    books = book_query.paginate(page=book_page, per_page=per_page, error_out=False)

    # Author search
    author_query = Author.query
    if author_search_query:
        author_query = author_query.filter(Author.name.ilike(f'%{author_search_query}%'))
    authors = author_query.paginate(page=author_page, per_page=per_page, error_out=False)

    # Get latest books for the current user
    if current_user.is_authenticated:
        latest_books = Book.query.join(UserBook).filter(UserBook.user_id == current_user.id).order_by(desc(UserBook.read_date)).limit(5).all()
        user_authors = Author.query.join(Book).join(UserBook).filter(UserBook.user_id == current_user.id).distinct().limit(5).all()
    else:
        latest_books = []
        user_authors = []

    return render_template('index.html', 
                           books=books, 
                           authors=authors, 
                           book_search_query=book_search_query, 
                           author_search_query=author_search_query,
                           latest_books=latest_books,
                           user_authors=user_authors)

@bp.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Fetch recent activities
    recent_activities = []
    
    # Recent books read
    recent_books = UserBook.query.filter_by(user_id=user.id).filter(UserBook.read_date.isnot(None)).order_by(UserBook.read_date.desc()).limit(5).all()
    for user_book in recent_books:
        recent_activities.append({
            'type': 'book_read',
            'book': user_book.book,
            'timestamp': datetime.combine(user_book.read_date, datetime.min.time())
        })
    
    # Recent lists created
    recent_lists = List.query.filter_by(user_id=user.id).order_by(List.id.desc()).limit(5).all()
    for list_item in recent_lists:
        recent_activities.append({
            'type': 'list_created',
            'list': list_item,
            'timestamp': datetime.fromtimestamp(list_item.id)  # Assuming id is a Unix timestamp
        })
    
    # Recent posts
    recent_posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).limit(5).all()
    for post in recent_posts:
        recent_activities.append({
            'type': 'post_created',
            'post': post,
            'timestamp': post.timestamp
        })
    
    # Sort all activities by timestamp (most recent first)
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Standardize timestamps
    for activity in recent_activities:
        activity['timestamp'] = activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('profile.html', user=user, recent_activities=recent_activities[:10])

@bp.route('/profile_image/<int:user_id>')
def profile_image(user_id):
    user = User.query.get_or_404(user_id)
    if user.profile_image:
        return send_file(BytesIO(user.profile_image), mimetype='image/jpeg')
    else:
        return send_file('static/images/default-profile.png', mimetype='image/png')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home.index'))

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Add logic for handling GET and POST requests
    return render_template('edit_profile.html')

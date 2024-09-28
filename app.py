import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Book, Author, List, UserBook
from functools import wraps
from sqlalchemy import func
from flask_migrate import Migrate
from routes import book_routes, author_routes, list_routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    db.init_app(app)
    migrate = Migrate(app, db)
    
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(author_routes.bp)
    app.register_blueprint(list_routes.bp)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_request
    def before_request():
        g.user = current_user

    @app.route('/')
    def index():
        latest_books = []
        user_authors = []
        books = None
        authors = None

        if current_user.is_authenticated:
            latest_books = Book.query.join(UserBook).filter(
                UserBook.user_id == current_user.id).order_by(
                    Book.id.desc()).limit(5).all()
            user_authors = Author.query.join(Book).join(UserBook).filter(
                UserBook.user_id == current_user.id).distinct().all()

        book_search_query = request.args.get('book_search', '')
        author_search_query = request.args.get('author_search', '')

        if book_search_query:
            book_page = request.args.get('book_page', 1, type=int)
            book_per_page = 10
            book_query = Book.query.filter(
                Book.title.ilike(f'%{book_search_query}%'))
            books = book_query.paginate(page=book_page,
                                        per_page=book_per_page,
                                        error_out=False)

        if author_search_query:
            author_page = request.args.get('author_page', 1, type=int)
            author_per_page = 10
            authors_query = Author.query.filter(
                Author.name.ilike(f'%{author_search_query}%'))
            authors = authors_query.paginate(page=author_page,
                                             per_page=author_per_page,
                                             error_out=False)

        return render_template('index.html',
                               latest_books=latest_books,
                               user_authors=user_authors,
                               books=books,
                               book_search_query=book_search_query,
                               authors=authors,
                               author_search_query=author_search_query)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))
            flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user:
                flash('Username already exists')
            else:
                new_user = User(username=username, email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('index'))
        return render_template('register.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

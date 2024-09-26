import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, g
from models import db, Book, Author, List, User, UserBook
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
from sqlalchemy import text, true
from flask_migrate import Migrate
from flask_talisman import Talisman
from urllib.parse import urlparse
from functools import wraps

def create_app():
    app = Flask(__name__)

    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "fallback_secret_key")
    app.logger.debug(f"SECRET_KEY: {app.config['SECRET_KEY'][:5]}...")

    db.init_app(app)

    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    csp = {
        'default-src': "'self'",
        'script-src': ["'self'", "https://cdn.jsdelivr.net"],
        'style-src': ["'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'"],
        'img-src': ["'self'", "https:", "data:"],
        'font-src': ["'self'", "https:", "data:"],
        'connect-src': "'self'",
        'upgrade-insecure-requests': ''
    }

    Talisman(app, content_security_policy=csp, force_https=True)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.logger.debug(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    from routes import book_routes, author_routes, list_routes
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(author_routes.bp)
    app.register_blueprint(list_routes.bp)

    @app.before_request
    def before_request():
        g.user = current_user

    @app.before_request
    def log_request_info():
        app.logger.debug(f"Request path: {request.path}")

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        app.logger.debug("Register route accessed")
        if current_user.is_authenticated:
            app.logger.debug("Authenticated user accessing register page, redirecting to index")
            return redirect(url_for('index'))
        if request.method == 'POST':
            app.logger.debug("Processing POST request for registration")
            try:
                username = request.form['username']
                email = request.form['email']
                password = request.form['password']

                user = User.query.filter_by(username=username).first()
                if user:
                    app.logger.warning(f"Registration attempt with existing username: {username}")
                    flash('Username already exists')
                    return redirect(url_for('register'))

                user = User.query.filter_by(email=email).first()
                if user:
                    app.logger.warning(f"Registration attempt with existing email: {email}")
                    flash('Email already exists')
                    return redirect(url_for('register'))

                new_user = User(username=username, email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                app.logger.info(f"New user registered successfully: {username}")
                flash('Registration successful')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Error during registration: {str(e)}')
                flash('An error occurred during registration. Please try again.')

        app.logger.debug("Rendering registration template")
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        app.logger.debug("Login route accessed")
        app.logger.debug(f"Session before login: {session}")

        if current_user.is_authenticated:
            app.logger.debug("User already authenticated, redirecting to index")
            return redirect(url_for('index'))

        if request.method == 'POST':
            app.logger.debug("Processing POST request")
            try:
                username = request.form['username']
                password = request.form['password']
                app.logger.debug(f"Login attempt for username: {username}")

                user = User.query.filter_by(username=username).first()
                if user:
                    app.logger.debug(f"User found: {username}")
                    if user.check_password(password):
                        app.logger.debug("Password check successful")
                        login_user(user)
                        app.logger.debug(f"Current user: {current_user.is_authenticated}")
                        app.logger.debug(f"login_user called for user: {username}")

                        session['user_id'] = user.id
                        app.logger.debug(f"Session after login: {session}")
                        app.logger.info(f"User logged in successfully: {username}")
                        next_page = request.args.get('next')
                        if not next_page or urlparse(next_page).netloc != '':
                            next_page = url_for('index')
                        app.logger.debug(f"Redirecting to: {next_page}")
                        return redirect(next_page)
                    else:
                        app.logger.warning(f"Invalid password for username: {username}")
                        flash('Invalid username or password')
                else:
                    app.logger.warning(f"User not found: {username}")
                    flash('Invalid username or password')
            except Exception as e:
                app.logger.error(f"Error during login: {str(e)}")
                flash('An error occurred during login. Please try again.')

        app.logger.debug("Rendering login template")
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        return redirect(url_for('index'))

    @app.route('/authors')
    @login_required
    def authors():
        return render_template('author/list.html', user_id=current_user.id, is_admin=current_user.is_admin)

    @app.route('/author/<int:id>')
    @login_required
    def author_detail(id):
        return render_template('author/detail.html', author_id=id)

    @app.route('/book/<int:id>')
    @login_required
    def book_detail(id):
        return render_template('book/detail.html', book_id=id)

    @app.route('/lists')
    @login_required
    def lists():
        return render_template('list/list.html', user_id=current_user.id, is_admin=current_user.is_admin)

    @app.route('/list/<int:id>')
    @login_required
    def list_detail(id):
        return render_template('list/detail.html', list_id=id)

    @app.route('/admin')
    @login_required
    def admin():
        if not current_user.is_admin:
            flash('You do not have permission to access the admin panel.')
            return redirect(url_for('index'))
        return render_template('admin/dashboard.html')

    @app.route('/admin/users', methods=['GET', 'POST'])
    @login_required
    def admin_users():
        if not current_user.is_admin:
            flash('You do not have permission to access the admin panel.')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            action = request.form.get('action')
            user_id = request.form.get('user_id')
            
            if action == 'delete':
                user = User.query.get(user_id)
                if user:
                    try:
                        # Remove user's books from all lists
                        BookList = db.Table('book_list', db.metadata, autoload_with=db.engine)
                        books_to_remove = db.session.query(BookList.c.book_id).join(Book).filter(Book.users.any(id=user.id)).subquery()
                        db.session.execute(BookList.delete().where(BookList.c.book_id.in_(books_to_remove)))
                        
                        # Remove user from all lists
                        for list in user.lists:
                            list.user_id = None
                        
                        # Delete all books associated with the user
                        Book.query.filter(Book.users.any(id=user.id)).delete(synchronize_session=False)
                        
                        # Delete the user
                        db.session.delete(user)
                        db.session.commit()
                        flash('User and associated data deleted successfully.')
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f"Error deleting user: {str(e)}")
                        flash('An error occurred while deleting the user. Please try again.')
                else:
                    flash('User not found.')
            
            elif action == 'toggle_admin':
                user = User.query.get(user_id)
                if user:
                    user.is_admin = not user.is_admin
                    db.session.commit()
                    flash(f"Admin status for {user.username} has been {'granted' if user.is_admin else 'revoked'}.")
                else:
                    flash('User not found.')
            
            return redirect(url_for('admin_users'))
        
        users = User.query.all()
        return render_template('admin/users.html', users=users)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

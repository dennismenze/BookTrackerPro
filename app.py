import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from models import db, Book, Author, List, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
from sqlalchemy import text
from flask_migrate import Migrate
from flask_talisman import Talisman
from urllib.parse import urlparse


def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY",
                                              "fallback_secret_key")

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Initialize Talisman for HTTPS
    Talisman(app, content_security_policy=None)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.logger.debug(
        f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Register blueprints
    from routes import book_routes, author_routes, list_routes
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(author_routes.bp)
    app.register_blueprint(list_routes.bp)

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
                        session.clear()  # Clear any existing session data
                        session['user_id'] = user.id
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
        return render_template('author/list.html')

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
        return render_template('list/list.html')

    @app.route('/list/<int:id>')
    @login_required
    def list_detail(id):
        return render_template('list/detail.html', list_id=id)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

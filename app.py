from flask import Flask, g
from flask_login import LoginManager, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_migrate import Migrate
from routes import book_routes, author_routes, list_routes, goal_routes, home_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(book_routes.bp, url_prefix='/book')
app.register_blueprint(author_routes.bp, url_prefix='/author')
app.register_blueprint(list_routes.bp, url_prefix='/list')
app.register_blueprint(goal_routes.bp, url_prefix='/goal')
app.register_blueprint(home_routes.bp)

login_manager = LoginManager()
login_manager.login_view = 'home.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    if not current_user.is_authenticated:
        user = User.query.filter_by(username='test').first()
        if user:
            login_user(user)
    g.user = current_user


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, g
from flask_login import LoginManager, login_user, current_user
from models import Book, UserBook, db, User, ReadingGoal, Author, List, BookList
from flask_migrate import Migrate
from routes import book_routes, author_routes, list_routes, goal_routes, home_routes
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import inspect

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

class CustomModelView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_export = True

admin = Admin(app, name='admin')
admin.add_view(CustomModelView(User, db.session, endpoint='users'))
admin.add_view(CustomModelView(Book, db.session, endpoint='books'))
userbooks = CustomModelView(UserBook, db.session, endpoint='userbooks')
userbooks.column_list = [c_attr.key for c_attr in inspect(UserBook).mapper.column_attrs]
admin.add_view(userbooks)
admin.add_view(CustomModelView(ReadingGoal, db.session, endpoint='readinggoals'))
admin.add_view(CustomModelView(Author, db.session, endpoint='authors'))
admin.add_view(CustomModelView(List, db.session, endpoint='lists'))
admin.add_view(CustomModelView(BookList, db.session, endpoint='booklists'))

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

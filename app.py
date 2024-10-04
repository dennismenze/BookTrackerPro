from flask import Flask, g
from flask_login import LoginManager, login_user, current_user
from models import Book, UserBook, db, User, ReadingGoal, Author, List, BookList
from flask_migrate import Migrate
from routes import book_routes, author_routes, list_routes, goal_routes, home_routes
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

db.init_app(app)
migrate = Migrate(app, db)


class CustomModelView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_export = True
    column_auto_select_related = True
    column_display_all_relations = True
    column_list = None  # This will display all columns including foreign keys
    column_exclude_list = ['password_hash']  # Exclude sensitive information
    form_excluded_columns = ['password_hash']  # Exclude sensitive information from forms

    def __init__(self, model, session, **kwargs):
        # Dynamically set column_list to include all columns
        self.column_list = [c.key for c in model.__table__.columns]
        super(CustomModelView, self).__init__(model, session, **kwargs)


admin = Admin(app, name='admin', template_mode='bootstrap3')
admin.add_view(CustomModelView(User, db.session, endpoint='users'))
admin.add_view(CustomModelView(Book, db.session, endpoint='books'))
admin.add_view(CustomModelView(UserBook, db.session, endpoint='userbooks'))
admin.add_view(CustomModelView(ReadingGoal, db.session, endpoint='readinggoals'))
admin.add_view(CustomModelView(Author, db.session, endpoint='authors'))
admin.add_view(CustomModelView(List, db.session, endpoint='lists'))
admin.add_view(CustomModelView(BookList, db.session, endpoint='booklists'))

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

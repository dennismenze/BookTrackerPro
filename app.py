from flask import Flask, g
from flask_login import LoginManager, login_user, current_user
from models import Book, UserBook, db, User, ReadingGoal, Author, List, BookList
from flask_migrate import Migrate
from routes import book_routes, author_routes, list_routes, goal_routes, home_routes
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import RelationshipProperty

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
    column_exclude_list = ['password_hash', 'profile_image']
    form_excluded_columns = ['password_hash', 'profile_image']

    def scaffold_list_columns(self):
        columns = super(CustomModelView, self).scaffold_list_columns()
        for name, prop in self.model.__mapper__.relationships.items():
            if isinstance(prop, RelationshipProperty) and prop.direction.name != 'MANYTOMANY':
                if hasattr(self.model, f'{name}_str'):
                    columns.append(f'{name}_str')
        return columns

    def __init__(self, model, session, **kwargs):
        super(CustomModelView, self).__init__(model, session, **kwargs)

        self.column_formatters = {}
        for name, prop in model.__mapper__.relationships.items():
            if isinstance(prop, RelationshipProperty) and prop.direction.name != 'MANYTOMANY':
                if hasattr(model, f'{name}_str'):
                    def formatter(view, context, model, name=name):
                        related_obj = getattr(model, name)
                        return str(related_obj) if related_obj else ''
                    self.column_formatters[f'{name}_str'] = formatter

class BookListModelView(CustomModelView):
    column_list = ('book_id', 'list_id', 'rank', 'book', 'list')
    column_labels = {
        'book_id': 'Book ID',
        'list_id': 'List ID',
        'rank': 'Rank',
        'book': 'Book',
        'list': 'List'
    }
    column_formatters = {
        'book': lambda v, c, m, p: f"{m.book.title} by {m.book.author.name}",
        'list': lambda v, c, m, p: f"{m.list.name} (User: {m.list.user.username})"
    }

admin = Admin(app, name='admin', template_mode='bootstrap3')
admin.add_view(CustomModelView(User, db.session, endpoint='users'))
admin.add_view(CustomModelView(Book, db.session, endpoint='books'))
admin.add_view(CustomModelView(UserBook, db.session, endpoint='userbooks'))
admin.add_view(CustomModelView(ReadingGoal, db.session, endpoint='readinggoals'))
admin.add_view(CustomModelView(Author, db.session, endpoint='authors'))
admin.add_view(CustomModelView(List, db.session, endpoint='lists'))
admin.add_view(BookListModelView(BookList, db.session, endpoint='booklists'))

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

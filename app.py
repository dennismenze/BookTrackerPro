import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from routes import book_routes, author_routes, list_routes
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(author_routes.bp)
    app.register_blueprint(list_routes.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/authors')
    def authors():
        return render_template('author/list.html')

    @app.route('/lists')
    def lists():
        return render_template('list/list.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask application")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

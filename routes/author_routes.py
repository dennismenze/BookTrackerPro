from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Author

bp = Blueprint('author', __name__)

@bp.route('/authors')
@login_required
def authors():
    return render_template('authors.html')

@bp.route('/author/<int:id>')
@login_required
def author_detail(id):
    return render_template('author/detail.html', author_id=id)

# Add other author-related routes here

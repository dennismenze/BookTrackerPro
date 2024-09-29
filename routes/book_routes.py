from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Book, UserBook

bp = Blueprint('book', __name__)

@bp.route('/book/<int:id>')
@login_required
def book_detail(id):
    return render_template('book/detail.html', book_id=id)

# Add other book-related routes here

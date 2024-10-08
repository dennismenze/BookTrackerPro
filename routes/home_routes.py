from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file, current_app, Response
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Book, Author, List, UserBook, Post, Translation
from sqlalchemy import or_, func, and_, case
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta
from io import BytesIO, StringIO
from flask_babel import _, get_locale
import csv
import io
import json
from fuzzywuzzy import fuzz

bp = Blueprint('home', __name__)

# Existing routes and functions remain unchanged

@bp.route('/my_read_books')
@login_required
def my_read_books():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # You can adjust this number as needed
    
    read_books = UserBook.query.filter_by(user_id=current_user.id).filter(UserBook.read_date.isnot(None)).order_by(UserBook.read_date.desc())
    
    paginated_books = read_books.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('my_read_books.html', books=paginated_books)

# Rest of the file remains unchanged

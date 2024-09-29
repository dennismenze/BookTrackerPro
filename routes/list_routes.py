from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, List

bp = Blueprint('list', __name__)

@bp.route('/lists')
@login_required
def lists():
    return render_template('list/list.html', user_id=current_user.id, is_admin=current_user.is_admin)

@bp.route('/list/<int:id>')
@login_required
def list_detail(id):
    return render_template('list/detail.html', list_id=id)

# Add other list-related routes here

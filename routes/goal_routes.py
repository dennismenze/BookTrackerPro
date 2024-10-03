from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, ReadingGoal, UserBook, Book
from datetime import datetime, date
from sqlalchemy import func

bp = Blueprint('goal', __name__)

@bp.route('/set_goal', methods=['GET', 'POST'])
@login_required
def set_goal():
    if request.method == 'POST':
        goal_type = request.form.get('goal_type')
        target = int(request.form.get('target'))
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

        if current_user.reading_goal:
            current_user.reading_goal.goal_type = goal_type
            current_user.reading_goal.target = target
            current_user.reading_goal.start_date = start_date
            current_user.reading_goal.end_date = end_date
        else:
            new_goal = ReadingGoal(user_id=current_user.id, goal_type=goal_type, target=target, start_date=start_date, end_date=end_date)
            db.session.add(new_goal)

        db.session.commit()
        flash('Reading goal set successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('goal/set_goal.html')

@bp.route('/goal_progress')
@login_required
def goal_progress():
    goal = current_user.reading_goal
    if not goal:
        return jsonify({'error': 'No reading goal set'}), 404

    today = date.today()
    if today < goal.start_date:
        return jsonify({'error': 'Reading goal has not started yet'}), 400
    if today > goal.end_date:
        today = goal.end_date

    total_days = (goal.end_date - goal.start_date).days + 1
    days_passed = (today - goal.start_date).days + 1
    
    if goal.goal_type == 'books':
        books_read = UserBook.query.filter(
            UserBook.user_id == current_user.id,
            UserBook.read_date.isnot(None),
            UserBook.book_id.in_(
                Book.query.with_entities(Book.id).filter(
                    func.date(Book.published_date) >= goal.start_date,
                    func.date(Book.published_date) <= today
                )
            )
        ).count()
        progress = (books_read / goal.target) * 100
        expected_progress = (days_passed / total_days) * 100
    else:  # pages
        pages_read = db.session.query(func.sum(Book.page_count)).join(UserBook).filter(
            UserBook.user_id == current_user.id,
            UserBook.read_date.isnot(None),
            func.date(Book.published_date) >= goal.start_date,
            func.date(Book.published_date) <= today
        ).scalar() or 0
        progress = (pages_read / goal.target) * 100
        expected_progress = (days_passed / total_days) * 100

    return jsonify({
        'goal_type': goal.goal_type,
        'target': goal.target,
        'progress': round(progress, 2),
        'expected_progress': round(expected_progress, 2),
        'start_date': goal.start_date.isoformat(),
        'end_date': goal.end_date.isoformat()
    })

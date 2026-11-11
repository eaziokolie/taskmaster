from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Task

main = Blueprint('main', __name__)

@main.route('/')
def index():
    filter_by = request.args.get('filter', 'all')
    priority = request.args.get('priority', 'all')

    query = Task.query
    if filter_by == 'active':
        query = query.filter_by(completed=False)
    elif filter_by == 'completed':
        query = query.filter_by(completed=True)

    if priority != 'all':
        query = query.filter_by(priority=priority)

    tasks = query.order_by(
        db.case({'high': 0, 'medium': 1, 'low': 2}, value=Task.priority),
        Task.created_at.desc()
    ).all()

    stats = {
        'total': Task.query.count(),
        'completed': Task.query.filter_by(completed=True).count(),
        'active': Task.query.filter_by(completed=False).count(),
        'high': Task.query.filter_by(priority='high', completed=False).count(),
    }

    return render_template('index.html', tasks=tasks, stats=stats,
                           filter_by=filter_by, priority=priority)

@main.route('/task/new', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')

        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('main.new_task'))

        task = Task(title=title, description=description, priority=priority)
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('task_form.html', task=None)

@main.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        task.title = request.form.get('title', '').strip()
        task.description = request.form.get('description', '').strip()
        task.priority = request.form.get('priority', 'medium')

        if not task.title:
            flash('Title is required.', 'danger')
            return redirect(url_for('main.edit_task', task_id=task_id))

        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('main.index'))

    return render_template('task_form.html', task=task)

@main.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(url_for('main.index'))

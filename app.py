from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database_manager import DatabaseManager
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os

encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    encryption_key = Fernet.generate_key()
    with open('.env', 'w') as f:
        f.write(f'ENCRYPTION_KEY={encryption_key.decode()}')
fernet = Fernet(encryption_key)


app = Flask(__name__)
app.secret_key = 'balto'  # Required for sessions

db = DatabaseManager("database.db")
db.create_tables()
BLOCKED_IPS = {'127.0.0.2'}  # 1 is yourself

def check_ip(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.remote_addr in BLOCKED_IPS:
            return jsonify({'error': 'blocked'}), 403
        return f(*args, **kwargs)
    return wrapper
@app.route('/')
@app.route('/api/your-endpoint', methods=['GET'])
@check_ip
def index():
    print('index function called')

    if 'username' in session:
        username = session['username']
        user = db.get_user_by_username(username)  # This fetches user details, including ID

        if user:
            user_id = user[0]# if user else None #extracts user id
            print(user_id)
            tasks = db.get_tasks_for_user(user_id)
            print(tasks)

            flash("tasks found", "success")
            return render_template('base.html', username=username, user=user, tasks=tasks)
    else:
        flash("tasks not found", "error")
        return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if db.verify_user(username, password):
            print("user verified, logging in...")
            if db.verify_user(username, password):
                user = db.get_user_by_username(username)
                print("hi")
                if user:
                    session['username'] = username
                    session['user_id'] = user[0]  # Store user ID in session
                    flash('Successfully logged in!', 'success')
                    print('Successfully logged in!', 'success')
            return render_template('base.html')
        else:
            print("user not valid")
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("/register")

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print("POST /register", username, password)

        if db.user_exists(username):
            print("user exists")
            flash('Username already exists', 'error')
            return redirect(url_for('login'))

        if db.add_user(username, password):
            print("user not exists, adding user")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error during registration', 'error')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    task_name = request.form.get('task_name')  # Get task name from form
    task_description = request.form.get('task_description')  # Get task description from form

    user_id = session.get('user_id')  # Retrieve user_id from session

    if not user_id:
        flash('You must be logged in to add a task.', 'error')

        return redirect(url_for('login'))

    # Call add_task method from DatabaseManager to insert task into the database
    task_added = db.add_task(task_name, task_description, user_id)

    if task_added:
        flash('Task added successfully!', 'success')
    else:
        flash('Failed to add task. Please try again.', 'error')

    return redirect(url_for('index'))  # Or redirect to the page displaying the user's tasks

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])  #int task id gets task id
def edit_task(task_id):
    # Get the task from the database by ID
    task = db.get_task_by_id(task_id)
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        task_name = request.form.get('task_name')
        task_description = request.form.get('task_description')

        # Update the task in the database
        task_updated = db.update_task(task_id, task_name, task_description)
        if task_updated:
            flash('Task updated successfully!', 'success')
        else:
            flash('Failed to update task. Please try again.', 'error')

        return redirect(url_for('index'))  # Redirect back to the main page

    return render_template('edit_task.html', task=task)  # Pass the task data to the form template

@app.route('/delete_task/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    task_deleted = db.delete_task(task_id)
    if task_deleted:
        flash('Task deleted successfully!', 'success')
    else:
        flash('Failed to delete task. Please try again.', 'error')
    return redirect(url_for('index'))  # Redirect to the main page


@app.route('/user/me', methods=['GET'])
def get_user_me():

    username = session.get('username')

    if not username:
        return "no such user", 404

    user = db.get_user_by_username(username)
    print(user)
    return "hi", 200


if __name__ == '__main__':
    app.run(debug=True)
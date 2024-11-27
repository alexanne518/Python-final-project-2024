from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database_manager import DatabaseManager

app = Flask(__name__)
app.secret_key = 'balto'  # Required for sessions

db = DatabaseManager("database.db")
db.create_tables()


@app.route('/')
def index():
    print('index function called')
    if 'username' in session:
        return render_template('base.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if db.verify_user(username, password):
            print("user verified, logging in...")
            session['username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
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


@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.get_json()
    task_name = data['task_name']
    task_description = data['task_description']

    db.add_task(task_name, task_description)
    return jsonify({'message':'task added successfully'})

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
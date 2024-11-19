from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from app.models.user import User  # Assuming User model exists in models/user.py
from app import db
from flask_login import login_user, login_required, current_user

# Create a Blueprint for user routes
users_bp = Blueprint('users', __name__)

# Route for registering a new user (renders registration page)
@users_bp.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate user data
        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('users.register_user'))

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'error')
            return redirect(url_for('users.register_user'))

        # Create and save the new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('users.login_user'))

    return render_template('register.html')

# Route for logging in a user (renders login page)
@users_bp.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # Check if user exists and password matches
        if user and user.password == password:  # In practice, compare hashed passwords
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('users.profile'))

        flash('Invalid credentials.', 'error')
        return redirect(url_for('users.login_user'))

    return render_template('login.html')

# Route for viewing user profile (requires login)
@users_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    # The logged-in user's information is available via `current_user`
    return render_template('profile.html', user=current_user)

# Route for updating user information (example)
@users_bp.route('/update', methods=['GET', 'POST'])
@login_required
def update_user():
    if request.method == 'POST':
        username = request.form['username']

        if not username:
            flash('Username is required.', 'error')
            return redirect(url_for('users.update_user'))

        current_user.username = username  # Update with any other fields as needed
        db.session.commit()
        flash('User information updated successfully.', 'success')
        return redirect(url_for('users.profile'))

    return render_template('update_user.html', user=current_user)

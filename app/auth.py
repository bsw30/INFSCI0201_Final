from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from app import db
from app.models import User

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', category='error')
            return redirect(url_for('auth.signup'))

        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # Assuming you have a `set_password` method

        # Add to DB
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful. Please log in.', category='success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Validate user
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):  # Assuming `check_password` method
            flash('Invalid login details. Please try again.', category='error')
            return redirect(url_for('auth.login'))

        # Log user in
        login_user(user, remember=remember)
        flash('Logged in successfully.', category='success')
        return redirect(url_for('main.dashboard'))  # Adjust according to your main route

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('auth.login'))


@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html')  # Assuming you have a profile.html template


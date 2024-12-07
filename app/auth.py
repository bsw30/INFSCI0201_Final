from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User, Organizer
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            return redirect(url_for('main.home'))
        else:
            flash('Please check your login details and try again.')
    
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        organizer_id = request.form.get('organizer_id')

        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            flash('Username or email address already exists')
            return redirect(url_for('auth.signup'))

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)

        if role == 'event_manager':
            if not organizer_id:
                flash('Event managers must be associated with an organizer')
                return redirect(url_for('auth.signup'))
            new_user.organizer_id = organizer_id

        db.session.add(new_user)
        db.session.commit()

        flash('Successfully signed up! Please log in.')
        return redirect(url_for('auth.login'))

    organizers = Organizer.query.all()
    return render_template('signup.html', organizers=organizers)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


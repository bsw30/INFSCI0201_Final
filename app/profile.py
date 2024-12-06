from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db

profile = Blueprint('profile', __name__)

@profile.route('/profile', methods=['GET'])
@login_required
def view_profile():
    return render_template('profile.html', user=current_user)

@profile.route('/profile/update', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')

        if not username or not email:
            flash('Username and email are required.', 'error')
            return redirect(url_for('profile.update_profile'))

        current_user.username = username
        current_user.email = email
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile.view_profile'))

    return render_template('update_profile.html', user=current_user)


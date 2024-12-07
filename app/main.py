from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/venues')
@login_required
def venues():
    return render_template('venues.html')

@main.route('/participants')
@login_required
def participants():
    return render_template('participants.html')

@main.route('/events')
@login_required
def events():
    return render_template('events.html')

@main.route('/reports')
@login_required
def reports():
    return render_template('reports.html')
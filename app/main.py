from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Event, User
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    events = Event.query.order_by(Event.date).limit(3).all()
    return render_template('index.html', events=events)

@main.route('/home')
@login_required
def home():
    events = Event.query.order_by(Event.date).all()
    return render_template('home.html', events=events)

@main.route('/search')
def search():
    query = request.args.get('query')
    if query:
        events = Event.query.filter(Event.title.ilike(f'%{query}%') | 
                                    Event.description.ilike(f'%{query}%') |
                                    Event.event_type.ilike(f'%{query}%') |
                                    Event.tags.ilike(f'%{query}%')).all()
    else:
        events = []
    return render_template('search_results.html', events=events, query=query)

@main.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    is_attending = current_user.is_authenticated and event.is_user_attending(current_user)
    can_manage = current_user.is_authenticated and current_user.is_event_manager() and current_user.id == event.organizer_id
    return render_template('event_details.html', event=event, current_time=datetime.now(), is_attending=is_attending, can_manage=can_manage)

@main.route('/event/<int:event_id>/signup', methods=['POST'])
@login_required
def signup_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.add_attendee(current_user):
        flash('You have successfully signed up for this event.', 'success')
    else:
        flash('You are already signed up for this event or the event has already started.', 'error')
    return redirect(url_for('main.event_details', event_id=event.id))

@main.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_signup(event_id):
    event = Event.query.get_or_404(event_id)
    if event.remove_attendee(current_user):
        flash('You have successfully cancelled your signup for this event.', 'success')
    else:
        flash('You are not signed up for this event or the event has already started.', 'error')
    return redirect(url_for('main.event_details', event_id=event.id))

@main.route('/profile')
@login_required
def profile():
    current_time = datetime.now()
    upcoming_events = Event.query.join(Event.attendees).filter(Event.attendees.any(id=current_user.id), Event.date > current_time).all()
    past_events = Event.query.join(Event.attendees).filter(Event.attendees.any(id=current_user.id), Event.date <= current_time).all()
    return render_template('profile.html', upcoming_events=upcoming_events, past_events=past_events)

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        bio = request.form.get('bio')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('main.settings'))

        if username != current_user.username and User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('main.settings'))

        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('main.settings'))

        current_user.username = username
        current_user.email = email
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.bio = bio

        if new_password:
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('main.settings'))
            current_user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash('Your settings have been updated.', 'success')
        return redirect(url_for('main.profile'))

    return render_template('settings.html')

@main.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if not current_user.is_event_manager():
        flash('You do not have permission to create events.')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M')
        location = request.form.get('location')
        event_type = request.form.get('event_type')
        tags = request.form.get('tags')
        image_url = request.form.get('image_url')

        new_event = Event(title=title, description=description, date=date, location=location,
                          event_type=event_type, tags=tags, image_url=image_url, organizer_id=current_user.id)
        db.session.add(new_event)
        db.session.commit()

        flash('Event created successfully.')
        return redirect(url_for('main.event_details', event_id=new_event.id))

    return render_template('create_event.html')

@main.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if not current_user.is_event_manager() or event.organizer_id != current_user.id:
        flash('You do not have permission to edit this event.')
        return redirect(url_for('main.event_details', event_id=event.id))

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.date = datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M')
        event.location = request.form.get('location')
        event.event_type = request.form.get('event_type')
        event.tags = request.form.get('tags')
        event.image_url = request.form.get('image_url')

        db.session.commit()
        flash('Event updated successfully.')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('edit_event.html', event=event)

@main.route('/cancel_event/<int:event_id>', methods=['POST'])
@login_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)
    if not current_user.is_event_manager() or event.organizer_id != current_user.id:
        flash('You do not have permission to cancel this event.')
        return redirect(url_for('main.event_details', event_id=event.id))

    db.session.delete(event)
    db.session.commit()
    flash('Event cancelled successfully.')
    return redirect(url_for('main.home'))

@main.route('/manager_dashboard')
@login_required
def manager_dashboard():
    if not current_user.is_event_manager():
        flash('You do not have permission to access the manager dashboard.')
        return redirect(url_for('main.home'))

    events = Event.query.filter_by(organizer_id=current_user.id).all()
    return render_template('manager_dashboard.html', events=events)


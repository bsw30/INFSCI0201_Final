from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, Response
from flask_login import login_required, current_user
from .models import Event, User, Organizer, Tag
from . import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
# from eventbrite import Eventbrite
# from .eventbrite_sync import EventbriteSync
import os
from icalendar import Calendar, Event as CalendarEvent
from urllib.parse import urlencode
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    available_tags = Tag.query.all()
    events = Event.query.order_by(Event.date.desc()).limit(3).all()
    return render_template('index.html', events=events, available_tags=available_tags)


@main.route('/home')
@login_required
def home():
    available_tags = Tag.query.all()
    events = filter_events(Event.query).order_by(Event.date).all()
    return render_template('home.html', events=events, available_tags=available_tags, is_event_manager=current_user.is_event_manager())


@main.route('/search')
def search():
    query = request.args.get('query')
    events = []
    if query:
        events = Event.query.filter(
            or_(
                Event.title.ilike(f'%{query}%'),
                Event.description.ilike(f'%{query}%'),
                Event.event_type.ilike(f'%{query}%'),
                Event.location.ilike(f'%{query}%'),
                Event.tags.any(Tag.name.ilike(f'%{query}%')) 
            )
        ).all()
    return render_template('search_results.html', events=events, query=query)

@main.route('/events')
@login_required
def events():
    events = filter_events(Event.query).order_by(Event.date).all()
    tags = Tag.query.all()
    return render_template('events.html', events=events, tags=tags)

def filter_events(query):
    event_type = request.args.get('event_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    location = request.args.get('location')
    tag = request.args.get('tag')  

    if event_type:
        query = query.filter(Event.event_type == event_type)
    if start_date:
        query = query.filter(Event.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Event.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    if location:
        query = query.filter(Event.location.ilike(f'%{location}%'))
    if tag: 
        query = query.filter(Event.tags.any(Tag.name == tag))

    return query


@main.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    is_attending = False
    can_manage = False
    registered_users = []
    
    if current_user.is_authenticated:
        is_attending = event.is_user_attending(current_user)
        can_manage = current_user.is_event_manager() and current_user.id == event.organizer_id
        if can_manage:
            registered_users = event.attendees.all()
    
        google_maps_api_key = 'AIzaSyDDJWUbZZL5Ln8ld0x6EUMQrdYblwgVDOI'
    
        return render_template('event_details.html', 
                         event=event,
                         current_time=datetime.now(),
                         is_attending=is_attending,
                         can_manage=can_manage,
                         registered_users=registered_users,
                         google_maps_api_key=google_maps_api_key)

@main.route('/event/<int:event_id>/signup', methods=['POST'])
@login_required
def signup_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.date < datetime.now():
        flash('This event has already passed. Signups are not allowed.', 'error')
    elif event.add_attendee(current_user):
        flash('You have successfully signed up for this event.', 'success')
    else:
        flash('You are already signed up for this event.', 'error')
    return redirect(url_for('main.event_details', event_id=event.id))

@main.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_signup(event_id):
    event = Event.query.get_or_404(event_id)
    if event.date < datetime.now():
        flash('This event has already passed. Cancellations are not allowed.', 'error')
    elif event.remove_attendee(current_user):
        flash('You have successfully cancelled your signup for this event.', 'success')
    else:
        flash('You are not signed up for this event.', 'error')
    return redirect(url_for('main.event_details', event_id=event.id))

@main.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    available_tags = Tag.query.all()  # Add this line
    if event.date < datetime.now():
        flash('This event has already passed. Editing is not allowed.', 'error')
        return redirect(url_for('main.event_details', event_id=event.id))
    if not current_user.is_event_manager() or event.organizer_id != current_user.id:
        flash('You do not have permission to edit this event.')
        return redirect(url_for('main.event_details', event_id=event.id))

    if request.method == 'POST':
        if update_event(event, request.form):
            flash('Event updated successfully.')
            return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('edit_event.html', event=event, available_tags=available_tags) 

@main.route('/profile')
@login_required
def profile():
    current_time = datetime.now()
    if current_user.is_event_manager():
        upcoming_events = Event.query.filter_by(organizer_id=current_user.id).filter(Event.date > current_time).order_by(Event.date).all()
        past_events = Event.query.filter_by(organizer_id=current_user.id).filter(Event.date <= current_time).order_by(Event.date.desc()).all()
    else:
        upcoming_events = Event.query.join(Event.attendees).filter(Event.attendees.any(id=current_user.id), Event.date > current_time).all()
        past_events = Event.query.join(Event.attendees).filter(Event.attendees.any(id=current_user.id), Event.date <= current_time).all()
    return render_template('profile.html', upcoming_events=upcoming_events, past_events=past_events)

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        if update_user_settings(current_user, request.form):
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
        new_event = create_new_event(request.form, current_user.id)
        if new_event:
            flash('Event created successfully.')
            return redirect(url_for('main.event_details', event_id=new_event.id))

    available_tags = Tag.query.all()
    google_maps_api_key = os.getenv('AIzaSyDDJWUbZZL5Ln8ld0x6EUMQrdYblwgVDOI')
    return render_template('create_event.html', available_tags=available_tags, google_maps_api_key=google_maps_api_key)

def create_new_event(form_data, organizer_id):
    tag_names = form_data.getlist('tags[]')
    tags = []
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tags.append(tag)

    new_event = Event(
        title=form_data.get('title'),
        description=form_data.get('description'),
        date=datetime.strptime(form_data.get('date'), '%Y-%m-%dT%H:%M'),
        location=form_data.get('location'),
        event_type=form_data.get('event_type'),
        tags=tags,
        image_url=form_data.get('image_url'),
        organizer_id=organizer_id
    )

    api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    new_event.geocode_location(api_key)
    
    
    
    db.session.add(new_event)
    db.session.commit()
    return new_event

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

# @main.route('/sync_eventbrite')
# @login_required
# def sync_eventbrite():
#     if not current_user.is_event_manager():
#         flash('You do not have permission to sync Eventbrite events.')
#         return redirect(url_for('main.home'))

#     try:
#         sync = EventbriteSync()
#         stats = sync.sync_events(current_user.organizer.id) 
        
#         if stats['new'] > 0:
#             flash(f'Successfully imported {stats["new"]} events from Eventbrite.')
#         else:
#             flash('No new events found on Eventbrite.')
            
#     except Exception as e:
#         print(f"Eventbrite sync error: {str(e)}")
#         flash(f'Error syncing Eventbrite events: {str(e)}', 'error')

#     return redirect(url_for('main.home'))

@main.route('/event/<int:event_id>/download.ics')
def download_ics(event_id):
    event = Event.query.get_or_404(event_id)
    cal = Calendar()
    cal_event = CalendarEvent()
    cal_event.add('summary', event.title)
    cal_event.add('description', event.description)
    cal_event.add('dtstart', event.date)
    cal_event.add('dtend', event.date + timedelta(hours=1))  # Assume 1-hour duration
    cal_event.add('location', event.location)
    cal.add_component(cal_event)

    response = Response(cal.to_ical(), mimetype='text/calendar')
    response.headers['Content-Disposition'] = f'attachment; filename={event.title.replace(" ", "_")}.ics'
    return response

@main.route('/event/<int:event_id>/add-to-google-calendar')
def add_to_google_calendar(event_id):
    event = Event.query.get_or_404(event_id)
    google_calendar_url = "https://www.google.com/calendar/render"
    params = {
        "action": "TEMPLATE",
        "text": event.title,
        "dates": f"{event.date.strftime('%Y%m%dT%H%M%S')}/{(event.date + timedelta(hours=1)).strftime('%Y%m%dT%H%M%S')}",
        "details": event.description,
        "location": event.location,
    }
    return redirect(f"{google_calendar_url}?{urlencode(params)}")


# Helper functions

def update_user_settings(user, form_data):
    if not check_password_hash(user.password_hash, form_data.get('current_password')):
        flash('Current password is incorrect.', 'error')
        return False

    if form_data.get('username') != user.username and User.query.filter_by(username=form_data.get('username')).first():
        flash('Username already exists.', 'error')
        return False

    if form_data.get('email') != user.email and User.query.filter_by(email=form_data.get('email')).first():
        flash('Email already exists.', 'error')
        return False

    user.username = form_data.get('username')
    user.email = form_data.get('email')
    user.first_name = form_data.get('first_name')
    user.last_name = form_data.get('last_name')
    user.bio = form_data.get('bio')

    new_password = form_data.get('new_password')
    if new_password:
        if new_password != form_data.get('confirm_password'):
            flash('New passwords do not match.', 'error')
            return False
        user.password_hash = generate_password_hash(new_password)

    db.session.commit()
    return True

def create_new_event(form_data, organizer_id):
    # Parse tags
    tag_names = form_data.getlist('tags')  # This will return a list of selected tag names
    tags = []
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
        tags.append(tag)

    new_event = Event(
        title=form_data.get('title'),
        description=form_data.get('description'),
        date=datetime.strptime(form_data.get('date'), '%Y-%m-%dT%H:%M'),
        location=form_data.get('location'),
        event_type=form_data.get('event_type'),
        tags=tags,  # Now we're passing a list of Tag objects
        image_url=form_data.get('image_url'),
        organizer_id=organizer_id
    )
    db.session.add(new_event)
    db.session.commit()
    return new_event

def update_event(event, form_data):
    event.title = form_data.get('title')
    event.description = form_data.get('description')
    event.date = datetime.strptime(form_data.get('date'), '%Y-%m-%dT%H:%M')
    event.location = form_data.get('location')
    event.event_type = form_data.get('event_type')
    

    tag_names = form_data.getlist('tags[]')
    tags = []
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tags.append(tag)
    event.tags = tags
    
    event.image_url = form_data.get('image_url')
    db.session.commit()
    return True





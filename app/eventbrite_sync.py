# import requests
# import os
# from datetime import datetime
# from .models import Event
# from . import db

# class EventbriteSync:
#     def __init__(self):
#         self.token = os.environ.get('EVENTBRITE_OAUTH_TOKEN')
#         self.api_url = 'https://www.eventbriteapi.com/v3'
        
#     def sync_events(self):
#         stats = {'new': 0, 'failed': 0}
        
#         try:
#             print("Making API request to Eventbrite...")
#             headers = {
#                 'Authorization': f'Bearer {self.token}',
#             }
            
#             # Search for public events
#             search_url = f'{self.api_url}/events/search/'
#             params = {
#                 'token': self.token,
#                 'sort_by': 'date',
#                 'location.address': 'San Francisco',  # You can change this to any location
#                 'expand': 'venue,logo'
#             }
            
#             events_response = requests.get(search_url, params=params)
            
#             print(f"Events Response Status: {events_response.status_code}")
            
#             if events_response.status_code == 200:
#                 events_data = events_response.json()
#                 events = events_data.get('events', [])
#                 print(f"Found {len(events)} events")
                
#                 for event_data in events:
#                     try:
#                         existing_event = Event.query.filter_by(eventbrite_id=event_data['id']).first()
                        
#                         if existing_event is None:
#                             new_event = Event(
#                                 title=event_data['name']['text'],
#                                 description=event_data.get('description', {}).get('text', 'No description available'),
#                                 date=datetime.strptime(event_data['start']['local'], '%Y-%m-%dT%H:%M:%S'),
#                                 location=event_data.get('venue', {}).get('address', {}).get('localized_address_display', 'Location TBA'),
#                                 event_type='Eventbrite Event',
#                                 organizer_id=1,  # Set a default organizer_id or remove if not needed
#                                 image_url=event_data.get('logo', {}).get('url'),
#                                 eventbrite_id=event_data['id']
#                             )
#                             db.session.add(new_event)
#                             stats['new'] += 1
#                             print(f"Added new event: {new_event.title}")
#                     except Exception as e:
#                         print(f"Error processing event: {str(e)}")
#                         stats['failed'] += 1
#                         continue
                
#                 try:
#                     db.session.commit()
#                     print(f"Sync complete. Added {stats['new']} events.")
#                 except Exception as e:
#                     print(f"Error committing to database: {str(e)}")
#                     db.session.rollback()
#                     stats['failed'] += 1
#             else:
#                 print(f"Events API request failed with status: {events_response.status_code}")
#                 print(f"Error details: {events_response.text}")
            
#         except Exception as e:
#             print(f"Error in sync_events: {str(e)}")
#             db.session.rollback()
            
#         return stats
# Event Management System

## Overview
The Event Management System is a web-based application designed to simplify the planning and coordination of events. Built with Python and Flask, this system provides event organizers with tools to manage event scheduling, participant registration, venue booking, and reporting. By centralizing these functionalities, the system enhances efficiency, reduces administrative overhead, and improves the overall event experience.

## Features
- **Event Scheduling**: Create and manage events with specific dates, times, and venues.
- **Participant Management**: Invite participants, track RSVP status, and send automated reminders.
- **Venue Management**: Prevent scheduling conflicts by tracking venue availability.
- **Reporting and Feedback**: Generate visualized reports on attendance and participant feedback.
- **Secure Login**: Ensure sensitive information is protected with user authentication.

## System Architecture
- **Frontend**:
  - Designed with Flask templates (Jinja) for a responsive and user-friendly interface.
  - Validates user input and manages session states.
- **Backend**:
  - Includes modules for authentication, event management, participant tracking, and reporting.
- **Database**:
  - Built on a relational SQL database with SQLAlchemy for scalable and secure data storage.

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/bsw30/INFSCI0201_Final.git
   cd INFSCI0201_Final
   ```
2. **Set up a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up the database**:
   - Create a `.env` file with your database configuration.
   - Run database migrations:
     ```bash
     flask db init
     flask db migrate
     flask db upgrade
     ```
5. **Run the application**:
   ```bash
   flask run
   ```

## Usage
### Home Dashboard
- View upcoming events, notifications, and quick links to key features like "Create Event" and "My Events."

### Event Creation and Management
- Add details such as event name, date, time, and location.
- Manage events under "My Events" with visual status indicators.

### Participant Management
- Send invitations via email, track RSVP status, and send reminders.
- Participants can confirm attendance and provide feedback after events.

### Venue Booking
- Assign venues to events and avoid double bookings with automated conflict checks.

### Reporting and Feedback
- View event reports with visualized data on attendance and participant feedback.

## Contributing
We welcome contributions to improve the Event Management System. Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push to your fork:
   ```bash
   git push origin feature-name
   ```
4. Open a pull request detailing your changes.

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

## Contact
For questions or support, contact the maintainers:
- **Melinda Go**: mtg62@example.com
- **Brianna Williams**: bsw30@example.com
- **Abby Zimmerman**: asz18@example.com

from flask import Blueprint, request, jsonify
from app.models import db, ProblemReport  # Adjust imports based on your setup

report_routes = Blueprint('report_routes', __name__)

@report_routes.route('/report-problem', methods=['POST'])
def report_problem():
    problem_description = request.form.get('problemDescription')
    user_email = request.form.get('userEmail', 'Anonymous')

    # Save report in the database
    new_report = ProblemReport(description=problem_description, email=user_email)
    db.session.add(new_report)
    db.session.commit()

    return jsonify({'message': 'Thank you for reporting the problem!'}), 200

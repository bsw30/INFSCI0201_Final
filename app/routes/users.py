from flask import Blueprint, request, jsonify, session, redirect, url_for
from models import db, User

user_bp = Blueprint('user', __name__)

# Role definitions (stored separately, not in the model)
USER_ROLE = "user"
MANAGER_ROLE = "manager"

# Temporary dictionary to store roles (or use a database table if available)
user_roles = {}  # Example: {user_id: "manager"}


# User Registration
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', USER_ROLE)  # Default role is "user"

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)  # Use User's set_password method
    db.session.add(new_user)
    db.session.commit()

    # Assign role after user creation
    user_roles[new_user.id] = role

    return jsonify({'message': 'User registered successfully', 'role': role}), 201


# User Login
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):  # Use User's check_password method
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_id'] = user.id
    session['user_role'] = user_roles.get(user.id, USER_ROLE)  # Default to "user" if no role

    return jsonify({'message': 'Login successful', 'role': session["user_role"]}), 200


# User Logout
@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    return jsonify({'message': 'Logout successful'}), 200


# Get Current User Info
@user_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.get(user_id)
    role = session.get('user_role', USER_ROLE)

    return jsonify({
        'username': user.username,
        'email': user.email,
        'role': role
    }), 200


# Check User Role
def is_manager():
    return session.get('user_role') == MANAGER_ROLE

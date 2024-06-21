from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, flash
from pymongo import MongoClient
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config.from_pyfile('config.py')
app.config['SECRET_KEY'] = 'xyz1234nbg789ty8inmcv2134'

client = MongoClient('mongodb://localhost:27017/')
db = client['user_login_system']
users_collection = db['users']
events_collection = db['events']

def generate_user_id():
    user_number = random.randint(1, 1000)
    user_id = f"user{user_number}"
    return user_id

def generate_event_id():
    event_number = random.randint(1, 100)
    event_id = f"event{event_number}"
    return event_id

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    department = data.get('department')
    year = data.get('year')

    # You should hash the password before storing it in production
    # For simplicity, it's assumed to be hashed in your actual implementation

    user_id = generate_user_id()

    user_data = {
        '_id': user_id,
        'username': username,
        'email': email,
        'password': password,  # Remember to hash this in production
        'department': department,
        'year': year
    }

    try:
        users_collection.insert_one(user_data)
        return jsonify({'success': True}), 200
    except Exception as e:
        print("Error inserting data into MongoDB:", e)
        return jsonify({'success': False, 'error': 'Registration failed. Please try again later.'}), 500
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Input validation
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400

        user_data = users_collection.find_one({'email': email})

        if user_data:
            # Direct plaintext password comparison (not recommended for production)
            if password == user_data['password']:
                session['logged_in'] = True
                session['user_id'] = str(user_data['_id'])  # Convert ObjectId to string
                return jsonify({'success': True}), 200

        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

    return jsonify({'success': False, 'error': 'Method not allowed'}), 405


@app.route('/home')
def home():
    return send_from_directory('build', 'index.html')

@app.route('/comp')
def comp():
    return send_from_directory('build', 'index.html')

@app.route('/comp1')
def comp1():
    return send_from_directory('build', 'index.html')

@app.route('/comp2')
def comp2():
    return send_from_directory('build', 'index.html')

@app.route('/register_comp1', methods=['POST'])
def register_comp1():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        event_name = 'Competition 1'

        existing_registration = events_collection.find_one({'user_id': user_id, 'event_name': event_name})
        if existing_registration:
            flash('You have already registered for Competition 1.', 'info')
        else:
            username = users_collection.find_one({'_id': user_id})['username']
            event_id = generate_event_id()
            registration_data = {'_id': event_id, 'user_id': user_id, 'event_name': event_name, 'username': username}
            events_collection.insert_one(registration_data)
            flash('You have successfully registered for Competition 1.', 'success')

    else:
        flash('Please log in to register for Competition 1.', 'error')

    return redirect(url_for('comp1'))

@app.route('/register_comp2', methods=['POST'])
def register_comp2():
    if request.method == 'POST':
        if 'logged_in' in session and session['logged_in']:
            user_id = session['user_id']
            event_name = 'Competition 2'

            existing_registration = events_collection.find_one({'user_id': user_id, 'event_name': event_name})
            if existing_registration:
                flash('You have already registered for Competition 2.', 'info')
            else:
                username = users_collection.find_one({'_id': user_id})['username']
                event_id = generate_event_id()
                registration_data = {'_id': event_id, 'user_id': user_id, 'event_name': event_name, 'username': username}
                events_collection.insert_one(registration_data)
                flash('You have successfully registered for Competition 2.', 'success')
        else:
            flash('Please log in to register for Competition 2.', 'error')

        return redirect(url_for('comp2'))
    else:
        flash('Method not allowed for this route.', 'error')
        return redirect(url_for('comp2'))

@app.route('/dash')
def dash():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']

        user = users_collection.find_one({'_id': user_id})

        user_registrations = list(events_collection.find({'user_id': user_id}))

        return send_from_directory('build', 'index.html')
    else:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path and (path.startswith('static/') or path.startswith('api/')):
        return send_from_directory('build', path)
    return send_from_directory('build', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)

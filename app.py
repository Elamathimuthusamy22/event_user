# app.py
from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask import jsonify
from pymongo import MongoClient
import bcrypt
import random

app = Flask(__name__)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']
        department = request.form['department']  # New
        year = request.form['year'] 

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        user_id = generate_user_id()

        user_data = {'_id': user_id, 'username': username, 'password': hashed_password, 'email': email, 'department': department,  
            'year': year }
        try:
            users_collection.insert_one(user_data)
            return redirect(url_for('login'))
        except Exception as e:
            print("Error inserting data into MongoDB:", e)
            return "An error occurred while registering. Please try again later."

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        user_data = users_collection.find_one({'email': email})

        if user_data:
            if bcrypt.checkpw(password, user_data['password']):
                session['logged_in'] = True
                session['user_id'] = user_data['_id']
                return redirect(url_for('home')) 
        
        error = 'Invalid email or password. Please try again.'
        return render_template('login.html', error=error)
    
    return render_template('login.html')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/comp')
def comp():
    return render_template('comp.html')



@app.route('/comp1')
def comp1():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        event_name = 'Competition 1'

        already_registered = bool(events_collection.find_one({'user_id': user_id, 'event_name': event_name}))

        return render_template('comp1.html', logged_in=True, already_registered=already_registered)

    else:
        return render_template('comp1.html', logged_in=False)

@app.route('/comp2')
def comp2():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        event_name = 'Competition 2'

        already_registered = bool(events_collection.find_one({'user_id': user_id, 'event_name': event_name}))

        return render_template('comp2.html', logged_in=True, already_registered=already_registered)

    else:
        return render_template('comp2.html', logged_in=False)

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
        # Handle other HTTP methods (e.g., GET) appropriately
        flash('Method not allowed for this route.', 'error')
        return redirect(url_for('comp2'))  # Redirect to comp2 page for other methods
    
# @app.route('/dash')
# def dash():
#     return render_template('dash.html')
    

@app.route('/dash')
def dash():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']

        # Retrieve user details from the database
        user = users_collection.find_one({'_id': user_id})

        # Retrieve competitions the user has registered for
        user_registrations = list(events_collection.find({'user_id': user_id}))  # Convert cursor to list

        return render_template('dash.html', user=user, registrations=user_registrations)
    else:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))






if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'xyz1234nbg789ty8inmcv2134'
    app.run(debug=True)

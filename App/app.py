from flask import Flask, jsonify, request, render_template, session, redirect, url_for, flash
from pymongo import MongoClient
import json
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'zaza7531'
# app.secret_key = os.getenv('APP_SECRET_KEY')

# MongoDB connection setup
user = os.getenv('USER')
password = os.getenv('PASSWORD')
service = os.getenv('SERVICE')
database = os.getenv('DATABASE')
#mongo_uri = 'mongodb://ofek:ofek2002@localhost:27017/?authSource=Final-project'
mongo_uri = 'mongodb://ofek:ofek2002@mongodb.default.svc.cluster.local:27017/?authSource=Final-project'
# mongo_uri = f'mongodb://{user}:{password}@{service}:27017/?authSource={database}'

client = MongoClient(mongo_uri)
db = client['Final-project']
users_collection = db['users']
planets_collection = db['planets']
votes_collection = db['votes']

# Load planet data from JSON file
planets_file = os.path.join(os.path.dirname(__file__), 'planets.json')
with open(planets_file, 'r') as f:
    planets_data = json.load(f)

# Initialize the planets collection if empty
if planets_collection.count_documents({}) == 0:
    planets_collection.insert_many(planets_data)

# Routes
@app.route('/')
def index():
    if 'username' in session:
        flash("Registration completed", 'success')
        return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/planets')
def planets():
    if 'username' not in session:
        return redirect(url_for('index'))

    # If user hasn't voted, render the planets page
    planets = list(planets_collection.find({}))

    # Get vote counts for each planet
    for planet in planets:
        vote_count = votes_collection.count_documents({'planet_name': planet['Name']})
        planet['vote_count'] = vote_count

    return render_template('planets.html', planets=planets)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        if not username or not password:
            flash("Username and password are required", 'error')
            return redirect(url_for('register'))

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Check if username exists in the database
        existing_user = users_collection.find_one({'username': username})

        if existing_user:
            # Compare the provided hashed password with the stored hashed password
            if bcrypt.checkpw(password, existing_user['password']):
                # Allow registration if the same username and password combination exists
                flash("Username and password combination already exists", 'error')
                return redirect(url_for('register'))

        # Insert new user if username is unique or does not exist with this password
        users_collection.insert_one({'username': username, 'password': hashed_password})
        flash("Registration successful", 'success')
        return redirect(url_for('index'))  # Redirect to index after successful registration

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        user = users_collection.find_one({'username': username})
        if user and bcrypt.checkpw(password, user['password']):
            session['username'] = username
            return redirect(url_for('planets'))
        flash("Invalid username or password, please try again", "error")
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect(url_for('index'))

    # Check if the user has already voted
    user_voted = votes_collection.find_one({'voter': session['username']})
    if user_voted:
        flash("Sorry, but you already voted", 'error')
        return redirect(url_for('planets'))  # Redirect to planets page if user has voted

    if request.method == 'GET':
        planets = list(planets_collection.find({}))
        return render_template('vote.html', planets=planets)
    elif request.method == 'POST':
        data = request.form
        planet_name = data.get('planet_name')
        comment = data.get('reason')

        if not planet_name:
            return jsonify({"error": "Planet name not provided"}), 400

        planet = planets_collection.find_one({'Name': planet_name})
        if planet:
            # Update votes collection
            votes_collection.insert_one({
                'planet_name': planet_name,
                'comment': comment,
                'voter': session['username']
            })
            flash("Vote received successfully", 'success')
    else:
        flash("Planet not found", 'error')

    return redirect(url_for('planets'))

# API endpoints for JSON data
@app.route('/api/planets', methods=['GET'])
def get_planets_api():
    planets = list(planets_collection.find({}, {'_id': 0}))
    return jsonify(planets)

@app.route('/api/planet/<name>', methods=['GET'])
def get_planet_api(name):
    planet = planets_collection.find_one({'name': name}, {'_id': 0})
    if planet:
        return jsonify(planet)
    else:
        return jsonify({"error": "Planet not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
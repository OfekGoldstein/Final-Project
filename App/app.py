from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from pymongo import MongoClient
import json
import os
import bcrypt

app = Flask(__name__)
app.secret_key = 'zaza7531'

# MongoDB connection setup
client = MongoClient('mongodb://root:Mpg3o9TbNX@10.109.237.149:27017/Final_Project?authSource=admin')
db = client['Final_Project']
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
        return redirect(url_for('planets'))
    return render_template('index.html')

@app.route('/planets')
def planets():
    if 'username' not in session:
        return redirect(url_for('index'))
    planets = list(planets_collection.find({}))
    return render_template('planets.html', planets=planets)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        if not username or not password:
            return "Username and password are required", 400

        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return "Username already exists", 400

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        users_collection.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('index'))
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
        return "Invalid username or password", 400
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        planets = list(planets_collection.find({}))
        return render_template('vote.html', planets=planets)
    elif request.method == 'POST':
        data = request.form
        planet_name = data.get('planet_name')
        comment = data.get('comment')

        if not planet_name:
            return jsonify({"error": "Planet name not provided"}), 400

        planet = planets_collection.find_one({'name': planet_name})
        if planet:
            votes_collection.update_one(
                {'planet_name': planet_name},
                {'$inc': {'votes': 1}, '$push': {'comments': comment}},
                upsert=True
            )
            return jsonify({"message": f"Voted for {planet_name}"}), 200
        else:
            return jsonify({"error": "Planet not found"}), 404

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
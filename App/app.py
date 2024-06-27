from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import json
import os

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['Final_Project']  # Replace with your database name
users_collection = db['users']
planets_collection = db['planets']
votes_collection = db['votes']

# Load planet data from JSON file
planets_file = os.path.join(os.path.dirname(__file__), 'planets.json')
with open(planets_file, 'r') as f:
    planets_data = json.load(f)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/planets')
def planets():
    return render_template('planets.html', planets=planets_data)

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'GET':
        return render_template('vote.html', planets=planets_data)
    elif request.method == 'POST':
        try:
            data = request.json
            planet_name = data.get('planet_name')

            if not planet_name:
                return jsonify({"error": "Planet name not provided in request body"}), 400

            planet = next((planet for planet in planets_data if planet['name'].lower() == planet_name.lower()), None)
            if planet:
                # Increment vote in MongoDB
                result = votes_collection.update_one({'planet_name': planet_name}, {'$inc': {'votes': 1}}, upsert=True)
                if result.modified_count == 0 and result.upserted_id is None:
                    return jsonify({"error": "Failed to update votes"}), 500

                return jsonify({"message": f"Voted for {planet_name}"}), 200
            else:
                return jsonify({"error": "Planet not found"}), 404

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return jsonify({"error": "Internal Server Error"}), 500

# API endpoints for JSON data
@app.route('/api/planets', methods=['GET'])
def get_planets_api():
    return jsonify(planets_data)

@app.route('/api/planet/<name>', methods=['GET'])
def get_planet_api(name):
    planet = next((planet for planet in planets_data if planet['name'].lower() == name.lower()), None)
    if planet:
        return jsonify(planet)
    else:
        return jsonify({"error": "Planet not found"}), 404

# User registration and authentication
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if user already exists
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    # Insert new user into MongoDB
    result = users_collection.insert_one({'username': username, 'password': password})
    if result.inserted_id:
        return jsonify({"message": "User registered successfully"}), 201
    else:
        return jsonify({"error": "Failed to register user"}), 500

# Voting comment storage
@app.route('/comment', methods=['POST'])
def comment():
    data = request.json
    planet_name = data.get('planet_name')
    comment = data.get('comment')

    if not planet_name or not comment:
        return jsonify({"error": "Planet name and comment are required"}), 400

    # Store comment in MongoDB
    result = votes_collection.update_one({'planet_name': planet_name}, {'$set': {'comment': comment}}, upsert=True)
    if result.modified_count == 0 and result.upserted_id is None:
        return jsonify({"error": "Failed to store comment"}), 500

    return jsonify({"message": "Comment stored successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
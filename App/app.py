from flask import Flask, jsonify, request, render_template
import json
import os

app = Flask(__name__)

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
                planet['votes'] = planet.get('votes', 0) + 1
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

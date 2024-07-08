from flask import Flask, jsonify, request, render_template, session, redirect, url_for, flash, get_flashed_messages
from pymongo import MongoClient
import json
import os
import bcrypt
from dotenv import load_dotenv

class FlaskApp:
    def __init__(self):
        load_dotenv()

        self.app = Flask(__name__)
        self.app.secret_key = 'zaza7531'
        # self.app.secret_key = os.getenv('APP_SECRET_KEY')
        
        user = os.getenv('USER')
        password = os.getenv('PASSWORD')
        service = os.getenv('SERVICE')
        database = os.getenv('DATABASE')
        mongo_uri = 'mongodb://ofek:ofek2002@mongodb.default.svc.cluster.local:27017/?authSource=Final-project'
        # mongo_uri = f'mongodb://{user}:{password}@{service}:27017/?authSource={database}'

        client = MongoClient(mongo_uri)
        self.db = client['Final-project']
        self.users_collection = self.db['users']
        self.planets_collection = self.db['planets']
        self.votes_collection = self.db['votes']

        planets_file = os.path.join(os.path.dirname(__file__), 'planets.json')
        with open(planets_file, 'r') as f:
            self.planets_data = json.load(f)

        if self.planets_collection.count_documents({}) == 0:
            self.planets_collection.insert_many(self.planets_data)

        self.add_routes()

    def add_routes(self):
        @self.app.route('/')
        def index():
            if 'username' in session:
                flash("Registration completed", 'success')
                return render_template('index.html')
            else:
                return render_template('index.html')

        @self.app.route('/planets')
        def planets():
            if 'username' not in session:
                return redirect(url_for('index'))
            
            planets = list(self.planets_collection.find({}))
        
            for planet in planets:
                vote_count = self.votes_collection.count_documents({'planet_name': planet['Name']})
                planet['vote_count'] = vote_count
                
            return render_template('planets.html', planets=planets)

        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password'].encode('utf-8')

                if not username or not password:
                    flash("Username and password are required", 'error')
                    return redirect(url_for('register'))

                hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

                existing_user = self.users_collection.find_one({'username': username})

                if existing_user:
                    if bcrypt.checkpw(password, existing_user['password']):
                        flash("Username and password combination already exists", 'error')
                        return redirect(url_for('register'))

                self.users_collection.insert_one({'username': username, 'password': hashed_password})
                flash("Registration successful", 'success')
                return redirect(url_for('index'))

            return render_template('register.html')

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password'].encode('utf-8')

                user = self.users_collection.find_one({'username': username})
                if user and bcrypt.checkpw(password, user['password']):
                    session['username'] = username
                    return redirect(url_for('planets'))
                flash("Invalid username or password, please try again", "error")
                return redirect(url_for('login'))
            return render_template('login.html')

        @self.app.route('/logout')
        def logout():
            session.pop('username', None)
            return redirect(url_for('index'))

        @self.app.route('/vote', methods=['GET', 'POST'])
        def vote():
            if 'username' not in session:
                return redirect(url_for('index'))
            
            user_voted = self.votes_collection.find_one({'voter': session['username']})
            if user_voted:
                flash("Sorry, but you already voted", 'error')
                return redirect(url_for('planets'))
            
            if request.method == 'GET':
                planets = list(self.planets_collection.find({}))
                return render_template('vote.html', planets=planets)
            elif request.method == 'POST':
                data = request.form
                planet_name = data.get('planet_name')
                comment = data.get('reason')

                if not planet_name:
                    return jsonify({"error": "Planet name not provided"}), 400

                planet = self.planets_collection.find_one({'Name': planet_name})
                if planet:
                    self.votes_collection.insert_one({
                        'planet_name': planet_name,
                        'comment': comment,
                        'voter': session['username']
                    })
                    flash("Vote received successfully", 'success')
            else:
                flash("Planet not found", 'error')

            return redirect(url_for('planets'))

        @self.app.route('/api/planets', methods=['GET'])
        def get_planets_api():
            planets = list(self.planets_collection.find({}, {'_id': 0}))
            return jsonify(planets)

        @self.app.route('/api/planet/<name>', methods=['GET'])
        def get_planet_api(name):
            planet = self.planets_collection.find_one({'name': name}, {'_id': 0})
            if planet:
                return jsonify(planet)
            else:
                return jsonify({"error": "Planet not found"}), 404

def create_app():
    return FlaskApp().app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
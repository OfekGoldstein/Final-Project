import pytest
from flask import session
from mongomock import MongoClient
from App.app import app

# Fixture to set up the test client and mock database
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    # Use mongomock to mock MongoDB collections
    with app.app_context():
        app.db_client = MongoClient()
        app.db = app.db_client['test_final_project']
        app.users_collection = app.db['users']
        app.votes_collection = app.db['votes']
        app.planets_collection = app.db['planets']

        # Initialize the planets collection if empty
        if app.planets_collection.count_documents({}) == 0:
            planets_data = [
                {"Name": "Mercury", "Mass": "3.30 x 10^23 kg", "Diameter": "4,880 km"},
                {"Name": "Venus", "Mass": "4.87 x 10^24 kg", "Diameter": "12,104 km"},
                {"Name": "Earth", "Mass": "5.97 x 10^24 kg", "Diameter": "12,742 km"},
                {"Name": "Mars", "Mass": "6.42 x 10^23 kg", "Diameter": "6,779 km"},
                {"Name": "Jupiter", "Mass": "1.90 x 10^27 kg", "Diameter": "139,820 km"},
                {"Name": "Saturn", "Mass": "5.68 x 10^26 kg", "Diameter": "116,460 km"},
                {"Name": "Uranus", "Mass": "8.68 x 10^25 kg", "Diameter": "50,724 km"},
                {"Name": "Neptune", "Mass": "1.02 x 10^26 kg", "Diameter": "49,244 km"}
            ]
            app.planets_collection.insert_many(planets_data)

    yield client

def test_register(client):
    response = client.post('/register', data={'username': 'testuser', 'password': 'testpassword'})
    assert response.status_code == 302  # Check for redirection
    follow_response = client.get('/', follow_redirects=True)
    assert b"Registration successful" in follow_response.data

def test_login(client):
    with client:
        client.post('/register', data={'username': 'testuser', 'password': 'testpassword'})
        response = client.post('/login', data={'username': 'testuser', 'password': 'testpassword'})
        assert response.status_code == 302  # Check for redirection
        with client.session_transaction() as session:
            assert 'username' in session

def test_logout(client):
    with client:
        client.post('/register', data={'username': 'testuser', 'password': 'testpassword'})
        client.post('/login', data={'username': 'testuser', 'password': 'testpassword'})
        response = client.get('/logout')
        assert response.status_code == 302  # Check for redirection
        with client.session_transaction() as session:
            assert 'username' not in session
import pytest
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

def test_vote(client):
    client.post('/register', data={'username': 'testuser', 'password': 'testpassword'})
    client.post('/login', data={'username': 'testuser', 'password': 'testpassword'})
    response = client.post('/vote', data={'planet_name': 'Earth', 'reason': 'It\'s my home!'})
    assert response.status_code == 302  # Check for redirection
    follow_response = client.get('/planets', follow_redirects=True)
    assert b"Vote received successfully" in follow_response.data

def test_get_planets_api(client):
    response = client.get('/api/planets')
    assert response.status_code == 200
    planets = response.get_json()
    assert len(planets) == 8  # Check that we have 8 planets

def test_get_planet_api(client):
    response = client.get('/api/planet/Earth')
    
    # Check response status code
    assert response.status_code == 200
    
    # Check that the response contains JSON data
    planet = response.get_json()
    assert planet is not None
    assert isinstance(planet, dict)
    
    # Check specific attributes of the planet
    assert planet['Name'] == 'Earth'
    assert planet['Mass'] == '5.97 x 10^24 kg'
    assert planet['Diameter'] == '12,742 km'
    
    # Add more assertions as needed for other attributes of the planet
    assert 'Average Distance from the Center of the Galaxy' in planet
    assert 'Average Surface Temperature' in planet
    # Add more assertions as per your application's planet data structure
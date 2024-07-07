import pytest
from app import app_test  # Importing app-test.py instead of app.py

@pytest.fixture
def client():
    app_test.config['TESTING'] = True
    with app_test.test_client() as client:
        yield client

def test_register(client):
    # Test registration endpoint
    response = client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'Registration successful' in response.data

def test_login(client):
    # Test login endpoint
    response = client.post('/login', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'Welcome' in response.data

def test_vote(client):
    # Test voting endpoint
    response = client.post('/vote', data=dict(
        planet_name='Earth',
        reason='Test vote'
    ), follow_redirects=True)
    assert b'Vote received successfully' in response.data

def test_logout(client):
    # Test logout endpoint
    response = client.get('/logout', follow_redirects=True)
    assert b'Login' in response.data

def test_error_handling(client):
    # Test error handling for missing planet name
    response = client.post('/vote', data=dict(
        reason='Test vote without planet name'
    ), follow_redirects=True)
    assert b'Planet name not provided' in response.data

    # Test error handling for invalid planet
    response = client.post('/vote', data=dict(
        planet_name='InvalidPlanet',
        reason='Test vote for invalid planet'
    ), follow_redirects=True)
    assert b'Planet not found' in response.data
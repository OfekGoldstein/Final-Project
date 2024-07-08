import pytest
from app import app  # Assuming app_test.py is your testing version of app.py
from mongomock import MongoClient

@pytest.fixture
def client(monkeypatch):
    app.config['TESTING'] = True

    # Mock MongoDB connection with mongomock
    monkeypatch.setattr('pymongo.MongoClient', MongoClient)

    with app.test_client() as client:
        yield client

def test_logout(client):
    # Test logout endpoint
    response = client.get('/logout', follow_redirects=True)
    assert b'Login' in response.data
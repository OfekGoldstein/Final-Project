from app import app
import pytest
import mongomock
import json
from pymongo import MongoClient

@pytest.fixture
def client(monkeypatch):
    app.config['TESTING'] = True

    # Mock MongoDB connection with mongomock
    monkeypatch.setattr('pymongo.MongoClient', MongoClient)

    with app.test_client() as client:
        yield client

def test_login(client):
    # Test login endpoint
    response = client.post('/login', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'Welcome' in response.data
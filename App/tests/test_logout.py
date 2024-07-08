import pytest
import app as flask_app
from mongomock import MongoClient

@pytest.fixture
def client(monkeypatch):
    flask_app.config['TESTING'] = True

    # Mock MongoDB connection with mongomock
    monkeypatch.setattr('pymongo.MongoClient', MongoClient)

    with flask_app.test_client() as client:
        yield client

def test_logout(client):
    # Test logout endpoint
    response = client.get('/logout', follow_redirects=True)
    assert b'Login' in response.data
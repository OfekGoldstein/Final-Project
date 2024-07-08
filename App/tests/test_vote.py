import pytest
from ..app import app  # Assuming app_test.py is your testing version of app.py
from mongomock import MongoClient

@pytest.fixture
def client(monkeypatch):
    app.config['TESTING'] = True

    # Mock MongoDB connection with mongomock
    monkeypatch.setattr('pymongo.MongoClient', MongoClient)

    with app.test_client() as client:
        yield client

def test_vote(client):
    # Test voting endpoint
    response = client.post('/vote', data=dict(
        planet_name='Earth',
        reason='Test vote'
    ), follow_redirects=True)
    assert b'Vote received successfully' in response.data
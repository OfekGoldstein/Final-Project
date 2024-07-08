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

def test_vote(client):
    # Test voting endpoint
    response = client.post('/vote', data=dict(
        planet_name='Earth',
        reason='Test vote'
    ), follow_redirects=True)
    assert b'Vote received successfully' in response.data
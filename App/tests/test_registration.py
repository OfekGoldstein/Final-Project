import pytest
from App import app
from mongomock import MongoClient

@pytest.fixture
def client(monkeypatch):
    app.config['TESTING'] = True

    # Mock MongoDB connection with mongomock
    monkeypatch.setattr('pymongo.MongoClient', MongoClient)

    with app.test_client() as client:
        yield client

def test_register(client):
    # Test registration endpoint
    response = client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'Registration successful' in response.data
import pytest
from mongomock import MongoClient
from flask import Flask
from ..app import app as flask_app  # Assuming your Flask app instance is named 'app' in app.py

# Fixture to provide a test client for Flask app
@pytest.fixture
def client():
    # Setting up app for testing
    flask_app.config['TESTING'] = True

    with flask_app.test_client() as client:
        yield client

# Fixture to mock MongoDB connection using mongomock
@pytest.fixture(scope='function')
def mongo_client(request):
    client = MongoClient()
    
    # Setup teardown function to drop the database after each test
    def teardown():
        client.drop_database('test_db')

    request.addfinalizer(teardown)
    return client

# Fixture to provide the Flask app instance
@pytest.fixture
def app():
    return flask_app
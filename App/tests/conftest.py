import pytest
from mongomock import MongoClient
from App.app import create_app

@pytest.fixture
def client(monkeypatch):
    app = create_app()
    app.config['TESTING'] = True

    monkeypatch.setattr('pymongo.MongoClient', MongoClient)

    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def mongo_client(request):
    client = MongoClient()
    
    def teardown():
        client.drop_database('test_db')

    request.addfinalizer(teardown)
    return client

@pytest.fixture
def app():
    return create_app()
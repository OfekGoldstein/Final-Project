import pytest

def test_register(client):
    # Test registration endpoint
    response = client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'Registration successful' in response.data

    # Test registration with existing username
    response = client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'Username and password combination already exists' in response.data

    # Test registration without username or password
    response = client.post('/register', data=dict(
        username='',
        password=''
    ), follow_redirects=True)
    assert b'Username and password are required' in response.data
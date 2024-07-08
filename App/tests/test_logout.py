import pytest

def test_logout(client):
    # Test logout endpoint
    client.get('/logout', follow_redirects=True)
    response = client.get('/')
    assert b'Login' in response.data  # Check if redirected to login page
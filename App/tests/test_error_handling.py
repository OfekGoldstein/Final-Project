import pytest

def test_error_handling(client):
    # Test error handling for missing planet name
    response = client.post('/vote', data=dict(
        reason='Test vote without planet name'
    ), follow_redirects=True)
    assert b'Planet name not provided' in response.data

    # Test error handling for invalid planet
    response = client.post('/vote', data=dict(
        planet_name='InvalidPlanet',
        reason='Test vote for invalid planet'
    ), follow_redirects=True)
    assert b'Planet not found' in response.data
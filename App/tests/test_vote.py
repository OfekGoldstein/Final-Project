import pytest

def test_vote(client):
    # Test voting endpoint
    response = client.post('/vote', data=dict(
        planet_name='Earth',
        reason='Test vote'
    ), follow_redirects=True)
    assert b'Vote received successfully' in response.data

    # Test voting for the same planet twice
    response = client.post('/vote', data=dict(
        planet_name='Earth',
        reason='Test vote again'
    ), follow_redirects=True)
    assert b'Sorry, but you already voted' in response.data

    # Test voting for an invalid planet
    response = client.post('/vote', data=dict(
        planet_name='InvalidPlanet',
        reason='Test vote for invalid planet'
    ), follow_redirects=True)
    assert b'Planet not found' in response.data
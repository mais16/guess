import pytest
from server import app, players, scores
import json
from unittest.mock import patch
import random

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test."""
    # Setup
    players.clear()
    scores.clear()
    random.seed(42)  # Set seed for reproducible tests
    # Initialize test player
    players['TestPlayer'] = {'guesses': []}
    yield
    # Teardown
    players.clear()
    scores.clear()
    random.seed()  # Reset random seed

def test_landing_page_get(client):
    """Test the landing page GET request."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the number guessing game!' in response.data
    assert b'Enter your name:' in response.data
    assert b'Start Game' in response.data

def test_landing_page_post_empty_name(client):
    """Test landing page POST with empty name."""
    response = client.post('/', data={'player_name': ''})
    assert response.status_code == 200
    assert b'Welcome to the number guessing game!' in response.data

def test_landing_page_post_valid_name(client):
    """Test player registration through POST request."""
    response = client.post('/', data={'player_name': 'TestPlayer'})
    assert response.status_code == 302  # Redirect status code
    assert 'TestPlayer' in players
    assert players['TestPlayer']['guesses'] == []

def test_invite_page_without_session(client):
    """Test invite page without player session."""
    response = client.get('/game')
    assert response.status_code == 302  # Should redirect to landing page

def test_invite_page_with_session(client):
    """Test invite page with player session."""
    with client.session_transaction() as session:
        session['player_name'] = 'TestPlayer'
    response = client.get('/game')
    assert response.status_code == 200
    assert b'Hello, TestPlayer!' in response.data
    assert b'Guess numbers between 1 and 100' in response.data

def test_guess_number_without_session(client):
    """Test guess without player session."""
    with client.session_transaction() as session:
        session.clear()  # Ensure session is empty
    response = client.get('/guess/50')
    assert response.status_code == 302  # Redirect to landing page

@pytest.mark.parametrize("guess,expected_message", [
    (25, b'Too low!'),
    (75, b'Too High!'),
    (50, b'You guessed it right!')
])
def test_guess_number(client, guess, expected_message):
    """Test different guess scenarios."""
    with client.session_transaction() as session:
        session['player_name'] = 'TestPlayer'
    
    with patch('server.number_to_be_guessed', 50):
        response = client.get(f'/guess/{guess}')
        assert response.status_code == 200
        assert expected_message in response.data
        if guess != 50:  # For wrong guesses
            assert guess in players['TestPlayer']['guesses']
        else:  # For correct guess
            assert 'TestPlayer' in scores

def test_guess_number_sequence(client):
    """Test a sequence of guesses leading to correct answer."""
    with client.session_transaction() as session:
        session['player_name'] = 'TestPlayer'
    
    with patch('server.number_to_be_guessed', 50):
        # Make wrong guesses
        client.get('/guess/25')
        client.get('/guess/75')
        # Make correct guess
        response = client.get('/guess/50')
        assert response.status_code == 200
        assert b'You guessed it right!' in response.data
        assert scores['TestPlayer'] == 3  # 3 total guesses

@pytest.mark.parametrize("endpoint,method,data,expected_status", [
    ('/players', 'POST', {'name': 'NewPlayer'}, 201),
    ('/players', 'POST', {'name': 'NewPlayer'}, 400),  # Duplicate
    ('/players', 'POST', {'invalid': 'data'}, 400),    # Invalid data
    ('/players/NewPlayer', 'GET', None, 200),
    ('/players/NonExistentPlayer', 'GET', None, 404),
    ('/players/NewPlayer', 'PUT', {'guesses': [1, 2, 3]}, 200),
    ('/players/NonExistentPlayer', 'PUT', {'guesses': [1, 2, 3]}, 404),
    ('/players/NewPlayer', 'DELETE', None, 200),
    ('/players/NonExistentPlayer', 'DELETE', None, 404),
])
def test_player_crud_operations(client, endpoint, method, data, expected_status):
    """Test CRUD operations for players."""
    # Ensure NewPlayer exists for duplicate and other operations
    if endpoint == '/players' and method == 'POST' and expected_status == 400:
        client.post('/players', data=json.dumps({'name': 'NewPlayer'}), content_type='application/json')
    if endpoint.startswith('/players/NewPlayer') and method != 'POST':
        client.post('/players', data=json.dumps({'name': 'NewPlayer'}), content_type='application/json')
    
    if method == 'POST':
        response = client.post(endpoint, 
                             data=json.dumps(data),
                             content_type='application/json')
    elif method == 'GET':
        response = client.get(endpoint)
    elif method == 'PUT':
        response = client.put(endpoint,
                            data=json.dumps(data),
                            content_type='application/json')
    elif method == 'DELETE':
        response = client.delete(endpoint)
    
    assert response.status_code == expected_status
    
    # Additional assertions for specific operations
    if method == 'POST' and expected_status == 201 and data is not None:
        assert data['name'] in players
        assert players[data['name']]['guesses'] == []
    elif method == 'GET' and expected_status == 200 and data is not None:
        assert data['name'] in json.loads(response.data)
    elif method == 'PUT' and expected_status == 200 and data is not None:
        player_name = endpoint.split('/')[-1]  # e.g., 'NewPlayer'
        assert players[player_name]['guesses'] == data['guesses']
    elif method == 'DELETE' and expected_status == 200 and data is not None:
        player_name = endpoint.split('/')[-1]  # e.g., 'NewPlayer'
        assert player_name not in players

def test_scores_page_empty(client):
    """Test scores page with no scores."""
    response = client.get('/scores')
    assert response.status_code == 200
    assert b'Player Scores' in response.data
    assert b'Back to Game' in response.data

def test_scores_page_with_scores(client):
    """Test scores page with existing scores."""
    scores['Player1'] = 5
    scores['Player2'] = 3
    response = client.get('/scores')
    assert response.status_code == 200
    assert b'Player1' in response.data
    assert b'Player2' in response.data
    assert b'5' in response.data
    assert b'3' in response.data

def test_guess_number_score_recording(client):
    """Test that scores are properly recorded for players."""
    with client.session_transaction() as session:
        session['player_name'] = 'TestPlayer'
    
    with patch('server.number_to_be_guessed', 50):
        # First correct guess should record score
        response = client.get('/guess/50')
        assert response.status_code == 200
        assert 'TestPlayer' in scores
        assert scores['TestPlayer'] == 1
        
        # Second correct guess should not update score
        response = client.get('/guess/50')
        assert response.status_code == 200
        assert scores['TestPlayer'] == 1  # Score should remain the same

def test_scores_page_no_scores(client):
    """Test scores page with no scores."""
    # Ensure scores is empty
    scores.clear()
    response = client.get('/scores')
    assert response.status_code == 200
    assert b'Player Scores' in response.data
    assert b'No scores yet' in response.data
    assert b'<tr><td>' not in response.data  # No table rows should be present
    assert b'Back to Game' in response.data 
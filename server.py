from flask import Flask, request, session, redirect, url_for, jsonify, Response
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session support

number_to_be_guessed = random.randint(1, 100)
print(number_to_be_guessed)

# In-memory player storage for CRUD
players = {}

# Track scores: {player_name: score}
scores = {}

# Decorator for guess responses

def guess_decorator(function):
    def wrapper(number):
        result = function(number)
        # If the result is a Flask Response (like redirect), return it directly
        if isinstance(result, Response):
            return result
        return f"<h2 style='color:yellow'>{result}</h2>"
    return wrapper

@app.route('/', methods=['GET', 'POST'])
def landing_page():
    if request.method == 'POST':
        player_name = request.form.get('player_name')
        if player_name:
            session['player_name'] = player_name
            # Add player to in-memory store if not exists
            if player_name not in players:
                players[player_name] = {'guesses': []}
            return redirect(url_for('invite_page'))
    return '''
        <h1 style="text-align:center">Welcome to the number guessing game!</h1>
        <form method="post" style="text-align:center">
            <label>Enter your name:</label>
            <input type="text" name="player_name" required>
            <button type="submit">Start Game</button>
        </form>
    '''

@app.route('/game')
def invite_page():
    player_name = session.get('player_name')
    if not player_name:
        return redirect(url_for('landing_page'))
    return f'<h1 style="text-align:center">Hello, {player_name}! Guess numbers between 1 and 100</h1>' \
           '<img src="https://media.giphy.com/media/3o7aCSPqXE5C6T8tBC/giphy.gif">'

@app.route('/guess/<int:number>')
@guess_decorator
def play(number):
    player_name = session.get('player_name')
    if not player_name:
        return redirect(url_for('landing_page'))
    if player_name in players:
        players[player_name]['guesses'].append(number)
    if number < number_to_be_guessed:
        return "Too low! Guess again!<img style='width:300px' " \
               "src='https://media.giphy.com/media/jD4DwBtqPXRXa/giphy.gif'>"
    elif number > number_to_be_guessed:
        return "Too High! Guess again!<img style='width:300px'" \
               " src='https://media.giphy.com/media/3o6ZtaO9BZHcOjmErm/giphy.gif'>"
    else:
        # Record score if not already recorded
        if player_name not in scores:
            scores[player_name] = len(players[player_name]['guesses'])
        return "<h2 style='color:green'>You guessed it right!</h2>" \
               "<img style='width:300px' src='https://media.giphy.com/media/4T7e4DmcrP9du/giphy.gif'>"

# --- CRUD Endpoints for Players ---

@app.route('/players', methods=['GET'])
def get_players():
    return jsonify(players)

@app.route('/players', methods=['POST'])
def create_player():
    data = request.get_json()
    name = data.get('name')
    if name and name not in players:
        players[name] = {'guesses': []}
        return jsonify({'message': 'Player created', 'player': {name: players[name]}}), 201
    return jsonify({'error': 'Player already exists or invalid name'}), 400

@app.route('/players/<name>', methods=['GET'])
def read_player(name):
    player = players.get(name)
    if player:
        return jsonify({name: player})
    return jsonify({'error': 'Player not found'}), 404

@app.route('/players/<name>', methods=['PUT'])
def update_player(name):
    data = request.get_json()
    if name in players:
        players[name].update(data)
        return jsonify({'message': 'Player updated', 'player': {name: players[name]}})
    return jsonify({'error': 'Player not found'}), 404

@app.route('/players/<name>', methods=['DELETE'])
def delete_player(name):
    if name in players:
        del players[name]
        return jsonify({'message': 'Player deleted'})
    return jsonify({'error': 'Player not found'}), 404

# --- Score Table Route ---
@app.route('/scores')
def show_scores():
    if not scores:
        return '''
            <h2>Player Scores</h2>
            <p>No scores yet</p>
            <a href="/game">Back to Game</a>
        '''
    table_rows = "".join([
        f"<tr><td>{name}</td><td>{score}</td></tr>" for name, score in scores.items()
    ])
    return f'''
        <h2>Player Scores</h2>
        <table border="1" style="border-collapse:collapse;">
            <tr><th>Player</th><th>Score (Guesses)</th></tr>
            {table_rows}
        </table>
        <a href="/game">Back to Game</a>
    '''

if __name__ == "__main__":
    app.run(debug=True)

from flask import Blueprint, request, session, redirect, url_for, jsonify
from app.decorators import guess_decorator
from app.game import add_player, add_guess, record_score, get_players, get_scores, check_guess, reset_game, delete_player

main_bp = Blueprint('main', __name__)

# --- CRUD Routes ---
@main_bp.route('/players', methods=['GET'])
def get_all_players():
    players = get_players()
    return jsonify(players)

@main_bp.route('/players', methods=['POST'])
def create_player():
    data = request.get_json()
    player_name = data.get('name')
    if player_name:
        add_player(player_name)
        return jsonify({"message": f"Player {player_name} created successfully"}), 201
    return jsonify({"error": "Player name is required"}), 400

@main_bp.route('/players/<name>', methods=['DELETE'])
def remove_player(name):
    if name in get_players():
        delete_player(name)
        return jsonify({"message": f"Player {name} deleted successfully"})
    return jsonify({"error": "Player not found"}), 404

@main_bp.route('/players/<name>', methods=['PUT'])
def update_player(name):
    data = request.get_json()
    new_name = data.get('name')
    if name in get_players() and new_name:
        # Delete old player and create new one
        delete_player(name)
        add_player(new_name)
        return jsonify({"message": f"Player {name} updated to {new_name} successfully"})
    return jsonify({"error": "Player not found or new name not provided"}), 404

@main_bp.route('/')
def landing_page():
    return redirect(url_for('main.invite_page'))

@main_bp.route('/game', methods=['GET', 'POST'])
def invite_page():
    if request.method == 'POST':
        player_name = request.form.get('player_name')
        if player_name:
            session['player_name'] = player_name
            add_player(player_name)
            return redirect(url_for('main.invite_page'))
    
    player_name = session.get('player_name', '')
    message = session.pop('message', '')
    
    return f'''
        <h1 style="text-align:center">Welcome to the Number Guessing Game!</h1>
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <form method="post" style="text-align:center; margin-bottom: 30px;">
                <label style="font-size: 18px; margin-right: 10px;">Enter your name:</label>
                <input type="text" name="player_name" value="{player_name}" required 
                       style="padding: 8px; font-size: 16px; width: 200px;">
                <button type="submit" 
                        style="padding: 8px 20px; font-size: 16px; margin-left: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Set Name
                </button>
            </form>

            <div style="text-align:center; margin-bottom: 20px;">
                <img src="https://media.giphy.com/media/3o7aCSPqXE5C6T8tBC/giphy.gif">
            </div>

            {f'<h2 style="text-align:center">Hello, {player_name}!</h2>' if player_name else ''}
            
            <div style="text-align:center; margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                <h3 style="color: #2196F3; margin: 0;">Guess the number between 1 - 100</h3>
            </div>

            <div style="text-align:center; margin-top: 20px; font-size: 20px; font-weight: bold;">
                {message}
            </div>

            <div style="text-align:center; margin-top: 20px;">
                <form action="/guess" method="post">
                    <input type="number" name="guess" min="1" max="100" required 
                           style="padding: 10px; font-size: 16px; width: 100px; text-align: center;">
                    <button type="submit" 
                            style="padding: 10px 20px; font-size: 16px; margin-left: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Guess!
                    </button>
                </form>
            </div>

            <div style="text-align:center; margin-top: 20px;">
                <a href="/scores" style="text-decoration: none; color: #2196F3;">View Scores</a>
            </div>
        </div>
    '''

@main_bp.route('/guess', methods=['POST'])
@guess_decorator
def play():
    player_name = session.get('player_name')
    if not player_name:
        session['message'] = "Please enter your name first!"
        return redirect(url_for('main.invite_page'))
        
    guess = request.form.get('guess')
    if not guess:
        return "Please enter a number!"
    number = int(guess)
    add_guess(player_name, number)
    result = check_guess(number)
    if "guessed it right" in result:
        # Record the score and show the number of guesses
        record_score(player_name)
        guesses_count = len(get_players()[player_name]['guesses'])
        result = f"<h2 style='color:green'>You guessed it right in {guesses_count} tries!</h2><img style='width:300px' src='https://media.giphy.com/media/4T7e4DmcrP9du/giphy.gif'>"
        # Add play again button to the success message
        result += '''
            <div style="text-align:center; margin-top: 20px;">
                <form action="/play-again" method="post">
                    <button type="submit" 
                            style="padding: 10px 20px; font-size: 16px; background-color: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Play Again!
                    </button>
                </form>
            </div>
        '''
        return result
    else:
        session['message'] = result
        return redirect(url_for('main.invite_page'))

@main_bp.route('/play-again', methods=['POST'])
def play_again():
    reset_game()
    return redirect(url_for('main.invite_page'))

# --- Score Table Route ---
@main_bp.route('/scores')
def show_scores():
    scores = get_scores()
    table_rows = "".join([
        f'''
        <tr>
            <td>{name}</td>
            <td>{score}</td>
            <td>
                <button onclick="deleteScore('{name}')" 
                        style="padding: 5px 10px; font-size: 14px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Delete
                </button>
                <button onclick="updateScore('{name}')" 
                        style="padding: 5px 10px; font-size: 14px; background-color: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 10px;">
                    Update
                </button>
            </td>
        </tr>
        ''' for name, score in scores.items()
    ])
    return f'''
        <h2>Player Scores</h2>
        <table border="1" style="border-collapse:collapse; margin: 0 auto;">
            <tr>
                <th>Player</th>
                <th>Score (Guesses)</th>
                <th>Action</th>
            </tr>
            {table_rows}
        </table>
        <div style="text-align:center; margin-top: 20px;">
            <a href="/game" style="text-decoration: none; color: #2196F3;">Back to Game</a>
        </div>
        <script>
        function deleteScore(name) {{
            if (confirm('Are you sure you want to delete this player and their score?')) {{
                fetch(`/scores/${{name}}`, {{
                    method: 'DELETE'
                }})
                .then(response => response.json())
                .then(data => {{
                    alert(data.message);
                    window.location.reload();
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    alert('Error deleting player');
                }});
            }}
        }}

        function updateScore(name) {{
            if (confirm('Do you want to play a new game with this player?')) {{
                fetch(`/scores/${{name}}`, {{
                    method: 'PUT'
                }})
                .then(response => response.json())
                .then(data => {{
                    alert(data.message);
                    window.location.href = '/game';
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    alert('Error updating player');
                }});
            }}
        }}
        </script>
    '''

@main_bp.route('/scores/<name>', methods=['DELETE'])
def delete_score(name):
    if name in get_players():
        delete_player(name)  # This will delete both player and their score
        return jsonify({'message': f'Player {name} and their score deleted successfully'})
    return jsonify({'error': 'Player not found'}), 404

@main_bp.route('/scores/<name>', methods=['PUT'])
def update_score(name):
    if name in get_players():
        # Set the player name in session
        session['player_name'] = name
        # Reset the game for a new attempt
        reset_game()
        return jsonify({'message': f'Player {name} is ready for a new game'})
    return jsonify({'error': 'Player not found'}), 404 
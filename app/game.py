import random

# In-memory player storage for CRUD
players = {}

# Track scores: {player_name: score}
scores = {}

# Game state
number_to_be_guessed = random.randint(1, 100)

def reset_game():
    global number_to_be_guessed
    number_to_be_guessed = random.randint(1, 100)
    return number_to_be_guessed

def get_number():
    return number_to_be_guessed

def add_player(player_name):
    if player_name not in players:
        players[player_name] = {'guesses': []}

def add_guess(player_name, guess):
    if player_name in players:
        players[player_name]['guesses'].append(guess)

def record_score(player_name):
    if player_name in players:
        # Always update with the latest game's guesses
        scores[player_name] = len(players[player_name]['guesses'])
        # Clear the guesses for the next game
        players[player_name]['guesses'] = []

def delete_player(player_name):
    if player_name in players:
        del players[player_name]
    if player_name in scores:
        del scores[player_name]

def get_players():
    return players

def get_scores():
    return scores

def check_guess(number):
    if number < number_to_be_guessed:
        return "Too low! Guess again!"
    elif number > number_to_be_guessed:
        return "Too High! Guess again!"
    else:
        return "<h2 style='color:green'>You guessed it right!</h2><img style='width:300px' src='https://media.giphy.com/media/4T7e4DmcrP9du/giphy.gif'>" 
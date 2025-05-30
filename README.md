# Flask Higher-Lower Game

A web-based number guessing game built with Flask where players try to guess a random number between 1 and 100. The game keeps track of player scores and provides a fun, interactive experience with animated GIFs for feedback.

## Features

- Player registration with name
- Interactive number guessing game
- Visual feedback with animated GIFs
- Score tracking system
- RESTful API endpoints for player management
- Session-based player tracking
- Comprehensive test coverage

## Prerequisites

- Python 3.x
- Flask
- pytest (for running tests)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd web-development-flask-higher-lower-game
```

2. Install the required dependencies:
```bash
pip install flask pytest
```

## Running the Application

To start the game server:

```bash
python server.py
```

The application will be available at `http://localhost:5000`

## Game Rules

1. Enter your name on the landing page
2. Try to guess the random number between 1 and 100
3. Get feedback after each guess:
   - "Too low!" if your guess is below the target number
   - "Too High!" if your guess is above the target number
   - "You guessed it right!" when you find the correct number
4. Your score is recorded based on the number of guesses it took to find the correct number

## API Endpoints

The application provides the following RESTful API endpoints:

- `GET /players` - List all players
- `POST /players` - Create a new player
- `GET /players/<name>` - Get player details
- `PUT /players/<name>` - Update player information
- `DELETE /players/<name>` - Delete a player

## Running Tests

To run the test suite:

```bash
pytest test_server_pytest.py
```

The test suite includes:
- Landing page functionality
- Player registration
- Game logic
- Score tracking
- API endpoint testing
- Session handling
- Edge cases

## Project Structure

- `server.py` - Main application file containing all routes and game logic
- `test_server_pytest.py` - Test suite for the application
- `README.md` - Project documentation

## Contributing

Feel free to submit issues and enhancement requests! 
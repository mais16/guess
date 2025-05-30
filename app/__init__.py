from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'  # Needed for session support

    # Import and register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app 
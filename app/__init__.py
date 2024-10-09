from flask import Flask
from .routes import initialize_routes

def create_app():
    app = Flask(__name__)
    initialize_routes(app)
    return app
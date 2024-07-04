from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    JWTManager(app)

    with app.app_context():
        from app import routes
        routes.init_app(app)

    return app
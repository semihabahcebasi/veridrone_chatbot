from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    from app import database
    database.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["https://bahcebasisemiha1.wixstudio.com"]
            }
        },
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )
    from app import database
    database.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
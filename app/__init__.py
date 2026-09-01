from flask import Flask

from app.database import initialize_database


def create_app():
    app = Flask(__name__)

    initialize_database()

    from app.routes import main
    app.register_blueprint(main)

    return app
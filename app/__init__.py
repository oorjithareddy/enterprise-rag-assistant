from flask import Flask

from app.database import initialize_database


def create_app():
    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

    initialize_database()

    from app.routes import main
    app.register_blueprint(main)

    return app
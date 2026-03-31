from flask import Flask

from .config import Config
from .routes.main import main_bp
from .routes.upload import upload_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    return app

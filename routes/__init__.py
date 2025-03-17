from flask import Flask
from config import Config
from utils.logger import logger
from db.database import db_init


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    db_init()

    logger.info("app created")
    
    from .main import main_bp
    from .cases import cases_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(cases_bp, url_prefix="/cases")

    return app

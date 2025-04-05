import os
from flask import Flask
from config import Config
from utils.logger import logger
from db.database import db_init


def create_app():
    if not os.path.exists(Config.BACKUP_DIR):
        os.makedirs(Config.BACKUP_DIR)
    
    if not os.path.exists(Config.LOGS_DIR):
        os.makedirs(Config.LOGS_DIR)
    
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    db_init()

    logger.info("app created")
    
    from .main import main_bp
    from .cases import cases_bp
    from .backup import backup_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(cases_bp, url_prefix="/cases")

    return app

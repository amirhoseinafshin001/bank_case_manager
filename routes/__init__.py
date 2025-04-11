import os
import sys

from flask import Flask
from flask import render_template

from config import Config
from utils.logger import logger
from db.database import db_init



def create_app():
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    template_folder = resource_path("templates")

    if not os.path.exists(Config.BACKUP_DIR):
        os.makedirs(Config.BACKUP_DIR)
    
    app = Flask(__name__, template_folder=template_folder)
    app.config.from_object(Config)

    db_init()

    logger.info("app created")
    
    from .main import main_bp
    from .cases import cases_bp
    from .backup import backup_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(cases_bp, url_prefix="/cases")

    @app.errorhandler(404)
    def handle_404(e):
        from flask import request
        
        if request.path.startswith('/cases/'):
            case_id = request.path.split('/')[-1]
            return render_template('case_404.html', case_id=case_id), 404
        
        return render_template('404.html'), 404

    return app

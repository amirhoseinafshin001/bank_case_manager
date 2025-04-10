import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    DB_PATH = "database.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BACKUP_DIR = "backup/"
    LOGS_DIR = "logs/"

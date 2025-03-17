from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from config import Config
from utils.logger import logger
from db.models import Base


DB_URI = Config.SQLALCHEMY_DATABASE_URI
engine = create_engine(DB_URI)
Session = scoped_session(sessionmaker(bind=engine)) # instant session maker.


def db_init() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("database initialized successfully.")
    except Exception as e:
        logger.error(f"data base initialization error: {e}")

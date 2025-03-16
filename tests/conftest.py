import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base
from db.database import Session

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = TestingSession()
    
    Session.configure(bind=engine)

    yield session

    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)
from sqlalchemy.orm import declarative_base
# base class for models
Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config

# Database connection
SQLALCHEMY_DATABASE_URL = config("POSTGRES_DB_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# create session factory
DBSession = sessionmaker(bind=engine, autoflush=False)

# Dependency to get DB session
def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

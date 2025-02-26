from sqlalchemy.orm import declarative_base
# base class for models
Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from decouple import config

# Database connection
SQLALCHEMY_DATABASE_URL = config("POSTGRES_DB_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, poolclass=NullPool)

# create session factory
DBSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

# Dependency to get DB session
def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

from . import models, database
from .models import User, OAuthCredential
from .database import Base
# This will create the `issues` table in the database

Base.metadata.create_all(bind=database.engine)

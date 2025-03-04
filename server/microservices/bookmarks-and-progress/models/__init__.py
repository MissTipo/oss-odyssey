from . import models, database
from .models import UserIssue, ProgressStatus
from .database import Base
# This will create the `bookmarks` table in the database

Base.metadata.create_all(bind=database.engine)


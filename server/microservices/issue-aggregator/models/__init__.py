from . import models, database

# This will create the `issues` table in the database

models.Base.metadata.create_all(bind=database.engine)

# FastApi app instance to initiate the server

from fastapi import FastAPI
from grapql_server import graphql_app

app = FastAPI()

# Add the `/graphql` route and set the `graphql_app` as its route handler
app.include_router(graphql_app, prefix="/graphql")

from fastapi import FastAPI
from graphql_server import graphql_app

app = FastAPI()

# Add the `/graphql` route and set the `graphql_app` as its route handler
app.include_router(graphql_app, prefix="/graphql")

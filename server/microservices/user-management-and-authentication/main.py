from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
DATABASE_URL = os.getenv("USER_DB_URL", "sqlite:///./test.db")

from fastapi import FastAPI
from graphql_server import graphql_app
from middleware.auth import authMiddleware
from webhooks.webhook import router as webhook_router
from webhooks.oauth_callback import router as oauth_callback_router

app = FastAPI()

# Add the `authMiddleware` to the list of middleware
app.middleware(authMiddleware)

# Include your webhook routes
app.include_router(webhook_router)
app.include_router(oauth_callback_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the user authenticator API."}

# Add the `/graphql` route and set the `graphql_app` as its route handler
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


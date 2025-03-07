# main.py
from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
DATABASE_URL = os.getenv("BOOKMARKS_DB_URL", "sqlite:///./test.db")

from fastapi import FastAPI
from graphql_server import graphql_app

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bookmarking service is up!"}

app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

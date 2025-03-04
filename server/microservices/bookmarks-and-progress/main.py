# main.py
from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
DATABASE_URL = os.getenv("POSTGRES_DB_URL", "sqlite:///./test.db")

from fastapi import FastAPI
from graphql_server import graphql_app

app = FastAPI()

app.include_router(graphql_app, prefix="/graphql")


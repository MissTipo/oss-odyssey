# tests/tests.py
import os
import pytest
import json
import asyncio
from fastapi.testclient import TestClient

from main import app
from models.database import Base, engine, SessionLocal

# Re-create the database for testing
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Override the GraphQL context getter for testing
# This override ensures that every request gets a dummy userId (e.g., 1)
# and a fresh database session.
async def test_get_context(request):
    # Force a dummy userId for testing purposes.
    request.state.userId = 1
    db = SessionLocal()
    return {"request": request, "db": db, "userId": 1}

# Patch the graphql_app's context_getter to use our test version.
from graphql_server import graphql_app
graphql_app.context_getter = test_get_context

def test_create_bookmark():
    mutation = """
    mutation {
      createBookmark(input: {
        userId: 1,
        issueId: 42,
        status: to_do,
        prLink: "http://example.com/pr/1"
      }) {
        id
        userId
        issueId
        status
        prLink
      }
    }
    """
    response = client.post("/graphql", json={"query": mutation})
    data = response.json()
    assert "data" in data, f"Response error: {data.get('errors')}"
    bookmark = data["data"]["createBookmark"]
    assert bookmark["userId"] == 1
    assert bookmark["issueId"] == 42
    assert bookmark["status"] == "to_do"
    assert bookmark["prLink"] == "http://example.com/pr/1"

def test_get_bookmarks():
    query = """
    query {
      getBookmarks {
        id
        userId
        issueId
        status
        prLink
      }
    }
    """
    response = client.post("/graphql", json={"query": query})
    data = response.json()
    assert "data" in data, f"Response error: {data.get('errors')}"
    bookmarks = data["data"]["getBookmarks"]
    assert isinstance(bookmarks, list)
    # At least one bookmark should be present from previous tests.
    assert len(bookmarks) >= 1

def test_update_bookmark():
    # Create a new bookmark to update.
    mutation_create = """
    mutation {
      createBookmark(input: {
        userId: 1,
        issueId: 100,
        status: to_do,
        prLink: "http://example.com/pr/100"
      }) {
        id
      }
    }
    """
    response_create = client.post("/graphql", json={"query": mutation_create})
    data_create = response_create.json()
    bookmark_id = data_create["data"]["createBookmark"]["id"]
    
    mutation_update = f"""
    mutation {{
      updateBookmark(input: {{
        id: {bookmark_id},
        status: in_progress,
        prLink: "http://example.com/pr/updated"
      }}) {{
        id
        status
        prLink
      }}
    }}
    """
    response_update = client.post("/graphql", json={"query": mutation_update})
    data_update = response_update.json()
    updated = data_update["data"]["updateBookmark"]
    assert updated["id"] == bookmark_id
    assert updated["status"] == "in_progress"
    assert updated["prLink"] == "http://example.com/pr/updated"

def test_delete_bookmark():
    # Create a new bookmark to delete.
    mutation_create = """
    mutation {
      createBookmark(input: {
        userId: 1,
        issueId: 200,
        status: to_do,
        prLink: "http://example.com/pr/200"
      }) {
        id
      }
    }
    """
    response_create = client.post("/graphql", json={"query": mutation_create})
    data_create = response_create.json()
    bookmark_id = data_create["data"]["createBookmark"]["id"]
    
    mutation_delete = f"""
    mutation {{
      deleteBookmark(id: {bookmark_id}) {{
        id
      }}
    }}
    """
    response_delete = client.post("/graphql", json={"query": mutation_delete})
    data_delete = response_delete.json()
    deleted = data_delete["data"]["deleteBookmark"]
    assert deleted["id"] == bookmark_id

    # Verify the deleted bookmark is no longer returned.
    query = """
    query {
      getBookmarks {
        id
      }
    }
    """
    response_query = client.post("/graphql", json={"query": query})
    data_query = response_query.json()
    bookmarks = data_query["data"]["getBookmarks"]
    for b in bookmarks:
        assert b["id"] != bookmark_id


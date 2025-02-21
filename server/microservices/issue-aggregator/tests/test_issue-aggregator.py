import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import strawberry
from graphql_server.schemas.issue_schema import Issue, State, Source
from graphql_server.resolvers.issue_resolver import QueryResolver, MutationResolver
from models.models import Issues, Base
from models.database import get_db
from graphql_server.__init__ import schema  # Import actual schema
from main import app

# Load environment variables from .env file
load_dotenv()

# --- Test Database Setup ---
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

# client = GraphQLTestClient(schema)

@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for a test."""
    Base.metadata.create_all(bind=engine)  # Create tables
    session = TestingSessionLocal()
    yield session
    session.rollback()  # Clean up after test
    session.close()
    Base.metadata.drop_all(bind=engine)  # Drop tables after each test

# --- Create the Test Client ---
@pytest.fixture
def graphql_client(db_session):
    """Provides a test GraphQL client with the test DB session in context."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# --- Tests ---

def test_get_issues_empty(graphql_client):
    """Test that when no issues exist, an empty list is returned."""
    query = "{ issues { id title } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result
    assert result["data"]["issues"] == []

def test_get_issues_with_data(graphql_client, db_session):
    """Test that issues query returns the correct data from the database."""
    now = datetime.datetime.utcnow()
    
    # Insert test issues into the database
    issue1 = Issues(title="Test Issue 1", description="This is a test issue.", state=True, source="github")
    issue2 = Issues(title="Test Issue 2", description="This is another test issue.", state=False, source="gitlab")

    db_session.add_all([issue1, issue2])
    db_session.commit()

    query = """
    {
      issues {
        id
        title
        state
        source
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()

    assert "errors" not in result
    data = result["data"]["issues"]
    
    assert len(data) == 2
    assert data[0]["title"] == "Test Issue 1"
    assert data[0]["state"] == "OPEN"
    assert data[0]["source"] == "GITHUB"

def test_get_issue_by_id(graphql_client, db_session):
    """Test retrieving a single issue by ID."""
    now = datetime.datetime.utcnow()

    # Insert test issue
    issue = Issues(title="Sample Issue", description="A sample issue.", state=True, source="github")
    db_session.add(issue)
    db_session.commit()

    query = f"""
    {{
      issue(id: {issue.id}) {{
        id
        title
        state
        source
      }}
    }}
    """
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    
    assert "errors" not in result
    data = result["data"]["issue"]
    assert data["id"] == issue.id
    assert data["title"] == "Sample Issue"
    assert data["state"] == "OPEN"
    assert data["source"] == "GITHUB"


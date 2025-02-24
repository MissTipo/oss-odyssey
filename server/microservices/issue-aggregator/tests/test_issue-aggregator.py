import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import strawberry
from graphql_server.schemas.issue_schema import Issue, State, Source
from graphql_server.schemas.user_issue_schema import UserIssue, Status
from graphql_server.schemas.issue_label_schema import IssueLabelAssociation
from graphql_server.schemas.project_schema import Project
from graphql_server.schemas.label_schema import Label
from graphql_server.schemas.repo_schema import Repository
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


# --- Label Tests ---

def test_labels_empty(graphql_client):
    """Test that when no labels exist, an empty list is returned."""
    query = "{ labels { labelId name } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result
    assert result["data"]["labels"] == []

def test_create_update_delete_label(graphql_client, db_session):
    """Test creating, updating, and deleting a label."""
    # Create label
    mutation_create = """
    mutation {
      createLabel(name: "Bug", color: "#ff0000", description: "Bug label", repositoryId: 1) {
        labelId
        name
        color
        description
        repositoryId
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": mutation_create})
    result = response.json()
    assert "errors" not in result
    label = result["data"]["createLabel"]
    labelId = label["labelId"]
    assert label["name"] == "Bug"

    # Update label
    mutation_update = f"""
    mutation {{
      updateLabel(labelId: {labelId}, name: "Feature") {{
        labelId
        name
      }}
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_update})
    result = response.json()
    updated_label = result["data"]["updateLabel"]
    assert updated_label["name"] == "Feature"

    # Delete label
    mutation_delete = f"""
    mutation {{
      deleteLabel(labelId: {labelId})
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_delete})
    result = response.json()
    assert "errors" not in result
    assert "deleted successfully" in result["data"]["deleteLabel"]

# --- Repository Tests ---

def test_repositories_empty(graphql_client):
    """Test that when no repositories exist, an empty list is returned."""
    query = "{ repositories { id name } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result
    assert result["data"]["repositories"] == []

def test_create_update_delete_repository(graphql_client, db_session):
    """Test creating, updating, and deleting a repository."""
    # Create repository
    mutation_create = """
    mutation {
      createRepository(externalId:"123", name:"TestRepo", fullName:"Test/TestRepo", description:"A test repo", url:"http://example.com", source: GITHUB) {
        id
        name
        fullName
        description
        url
        source
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": mutation_create})
    result = response.json()
    assert "errors" not in result
    repo = result["data"]["createRepository"]
    repo_id = repo["id"]
    assert repo["name"] == "TestRepo"

    # Update repository
    mutation_update = f"""
    mutation {{
      updateRepository(id: {repo_id}, name:"UpdatedRepo") {{
        id
        name
      }}
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_update})
    result = response.json()
    updated_repo = result["data"]["updateRepository"]
    assert updated_repo["name"] == "UpdatedRepo"

    # Delete repository
    mutation_delete = f"""
    mutation {{
      deleteRepository(id: {repo_id})
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_delete})
    result = response.json()
    assert "errors" not in result
    assert "deleted successfully" in result["data"]["deleteRepository"]

# --- Project Tests ---

def test_projects_empty(graphql_client):
    """Test that when no projects exist, an empty list is returned."""
    query = "{ projects { projectId name } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result
    assert result["data"]["projects"] == []

def test_create_update_delete_project(graphql_client, db_session):
    """Test creating, updating, and deleting a project."""
    # Create project
    mutation_create = """
    mutation {
      createProject(name:"Test Project", description:"Project description", url:"http://example.com", source: GITHUB, repositoryId: 1, ownerId: 1) {
        projectId
        name
        description
        url
        source
        repositoryId
        ownerId
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": mutation_create})
    result = response.json()
    assert "errors" not in result
    project = result["data"]["createProject"]
    projectId = project["projectId"]
    assert project["name"] == "Test Project"

    # Update project
    mutation_update = f"""
    mutation {{
      updateProject(projectId: {projectId}, name:"Updated Project") {{
        projectId
        name
      }}
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_update})
    result = response.json()
    updated_project = result["data"]["updateProject"]
    assert updated_project["name"] == "Updated Project"

    # Delete project
    mutation_delete = f"""
    mutation {{
      deleteProject(projectId: {projectId})
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_delete})
    result = response.json()
    assert "errors" not in result
    assert "deleted successfully" in result["data"]["deleteProject"]

# --- UserIssue Tests ---

def test_user_issues_empty(graphql_client):
    """Test that when no user issues exist, an empty list is returned."""
    query = "{ userIssues { issueId issue } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result
    assert result["data"]["userIssues"] == []

def test_create_update_delete_user_issue(graphql_client, db_session):
    """Test creating, updating, and deleting a user issue."""
    # Create user issue
    mutation_create = """
    mutation {
      createUserIssue(issue: 1, projectId: 1, status: BACKLOG, prLink:"") {
        issueId
        issue
        projectId
        status
        prLink
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": mutation_create})
    result = response.json()
    assert "errors" not in result
    user_issue = result["data"]["createUserIssue"]
    user_issue_id = user_issue["issueId"]
    assert user_issue["status"] == "BACKLOG"

    # Update user issue
    mutation_update = f"""
    mutation {{
      updateUserIssue(issueId: {user_issue_id}, status: IN_PROGRESS, prLink:"http://pr.example.com") {{
        issue
        status
        prLink
      }}
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_update})
    result = response.json()
    updated_user_issue = result["data"]["updateUserIssue"]
    assert updated_user_issue["status"] == "IN_PROGRESS"
    assert updated_user_issue["prLink"] == "http://pr.example.com"

    # Delete user issue
    mutation_delete = f"""
    mutation {{
      deleteUserIssue(issueId: {user_issue_id})
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_delete})
    result = response.json()
    assert "errors" not in result
    assert "deleted successfully" in result["data"]["deleteUserIssue"]

# --- IssueLabel Association Tests ---

def test_issue_label_associations_empty(graphql_client):
    """Test that when no issue-label associations exist, an empty list is returned."""
    query = "{ issueLabelAssociations { id issueId labelId } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result
    assert result["data"]["issueLabelAssociations"] == []

def test_create_delete_issue_label_association(graphql_client, db_session):
    """Test creating and then deleting an issue-label association."""
    # Create issue label association
    mutation_create = """
    mutation {
      createIssueLabelAssociation(issueId: 1, labelId: 1) {
        id
        issueId
        labelId
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": mutation_create})
    result = response.json()
    assert "errors" not in result
    association = result["data"]["createIssueLabelAssociation"]
    association_id = association["id"]
    assert association["issueId"] == 1
    assert association["labelId"] == 1

    # Delete issue label association
    mutation_delete = f"""
    mutation {{
      deleteIssueLabelAssociation(id: {association_id})
    }}
    """
    response = graphql_client.post("/graphql", json={"query": mutation_delete})
    result = response.json()
    assert "errors" not in result
    assert "deleted successfully" in result["data"]["deleteIssueLabelAssociation"]

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

import os
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
from models.models import Issues, Base, Labels, Repositories
from models.database import get_db
from graphql_server.__init__ import schema  # Import actual schema
from main import app

# --- Test Database Setup ---
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

# client = GraphQLTestClient(schema)
def test_github_token():
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    assert token is not None, "GITHUB_TOKEN is not set"


@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for a test."""
    Base.metadata.create_all(bind=engine)  # Create tables
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()  # Clean up after test
    connection.close()
    Base.metadata.drop_all(bind=engine)  # Drop tables after each test

# --- Create the Test Client ---
@pytest.fixture
def graphql_client(db_session):
    """Provides a test GraphQL client with the test DB session in context."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# --- Tests issues ---

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

def test_refresh_issues(graphql_client, db_session):
    """
    Test refreshing issues from GitHub.
    (This mutation fetches issues from GitHub rather than relying solely on local data.)
    """
    mutation_refresh = """
    mutation {
      refreshIssues
    }
    """
    response = graphql_client.post("/graphql", json={"query": mutation_refresh})
    result = response.json()
    assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
    # Expect a success message
    assert "Issues refreshed successfully" in result["data"]["refreshIssues"]

    # Query issues after refresh.
    query = "{ issues { id title } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    issues = result["data"]["issues"]
    assert isinstance(issues, list)
    # Optionally, assert that some issues were fetched.
    # For now, we ensure that the list is returned.
    assert issues is not None



# --- Label Tests ---

def test_labels_empty(graphql_client):
    """Test that when no labels exist, an empty list is returned."""
    query = "{ labels { labelId name color description repositoryId } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result
    assert result["data"]["labels"] == []
    
def test_get_label_by_id(graphql_client, db_session):
    """Test retrieving a label by its unique ID."""
    # Insert a label into the database
    label = Labels(name="bug", color="#ff0000", description="Bug label", repository_id=1)
    db_session.add(label)
    db_session.commit()
    
    query = f"""
    {{
      label(labelId: {label.id}) {{
        labelId
        name
        color
        description
        repositoryId
      }}
    }}
    """
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result, result.get("errors")
    data = result["data"]["label"]
    assert data["name"] == "bug"
    assert data["color"] == "#ff0000"

def test_get_labels_by_repository(graphql_client, db_session):
    """Test retrieving labels by repository ID."""
    # Insert multiple labels
    label1 = Labels(name="bug", color="#ff0000", description="Bug label", repository_id=1)
    label2 = Labels(name="feature", color="#00ff00", description="Feature label", repository_id=1)
    label3 = Labels(name="docs", color="#0000ff", description="Documentation", repository_id=2)
    db_session.add_all([label1, label2, label3])
    db_session.commit()
    
    query = """
    {
      labelsByRepository(repositoryId: 1) {
        labelId
        name
        color
        description
        repositoryId
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result, result.get("errors")
    labels = result["data"]["labelsByRepository"]
    assert isinstance(labels, list)
    # Expect only the two labels with repository_id=1
    assert len(labels) == 2

def test_refresh_labels(graphql_client, db_session):
    """
    Test refreshing labels from GitHub.
    (This mutation fetches labels from GitHub rather than creating them manually.)
    """
    mutation_refresh = """
    mutation {
      refreshLabels(repositoryOwner: "apache", repositoryName: "airflow")
    }
    """
    response = graphql_client.post("/graphql", json={"query": mutation_refresh})
    result = response.json()
    # Since refreshLabels returns a string, we can check for a success message.
    assert "errors" not in result
    assert "Labels refreshed successfully" in result["data"]["refreshLabels"]

    # Query labels after refresh.
    query = "{ labels { labelId name color description repositoryId } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    labels = result["data"]["labels"]
    assert isinstance(labels, list)
    # Optionally, check that at least one label was fetched (if you know the remote repo has labels)
    # For now, just ensure that a list is returned.
    assert labels is not None


# --- Repository Tests ---

def test_repositories_empty(graphql_client):
    """Test that when no repositories exist, an empty list is returned."""
    query = "{ repositories { id name language } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result
    assert result["data"]["repositories"] == []

def test_get_repository_by_id(graphql_client, db_session):
    """Test retrieving a repository by its unique ID."""
    repo = Repositories(
        external_id="123",
        name="TestRepo",
        full_name="Test/TestRepo",
        description="A test repository",
        url="http://example.com",
        source="github",
        language="Python"
    )
    db_session.add(repo)
    db_session.commit()
    
    query = f"""
    {{
      repository(id: {repo.id}) {{
        id
        name
        language
      }}
    }}
    """
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result, result.get("errors")
    data = result["data"]["repository"]
    assert data["name"] == "TestRepo"
    assert data["language"] == "Python"

def test_get_repositories_by_source(graphql_client, db_session):
    """Test retrieving repositories filtered by source."""
    repo1 = Repositories(
        external_id="123",
        name="RepoGitHub",
        full_name="Test/RepoGitHub",
        description="A test repository",
        url="http://example.com",
        source="github",
        language="Python"
    )
    repo2 = Repositories(
        external_id="456",
        name="RepoGitLab",
        full_name="Test/RepoGitLab",
        description="Another test repository",
        url="http://example.com",
        source="gitlab",
        language="JavaScript"
    )
    db_session.add_all([repo1, repo2])
    db_session.commit()
    
    query = """
    {
      repositoriesBySource(source: GITHUB) {
        id
        name
        language
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    assert "errors" not in result, result.get("errors")
    repos = result["data"]["repositoriesBySource"]
    assert isinstance(repos, list)
    # Expect only the GitHub repository
    assert len(repos) == 1
    assert repos[0]["name"] == "RepoGitHub"

# Optionally, you can add a test for get_repositories_by_label.
# Since it fetches remote data, you may choose to skip it in unit tests.
@pytest.mark.skip(reason="Remote fetch not tested in unit tests")
def test_get_repositories_by_label(graphql_client):
    query = """
    {
      repositoriesByLabel(label: "hacktober") {
        id
        name
        language
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    repos = result["data"]["repositoriesByLabel"]
    assert isinstance(repos, list)

def test_refresh_repositories(graphql_client, db_session):
    """
    Test refreshing repositories from GitHub using a topic filter.
    (Repositories are fetched remotely rather than created manually.)
    Note: Since refreshRepositories returns a Repository object, we must provide a selection set.
    """
    mutation_refresh = """
    mutation {
      refreshRepositories(label: "hacktober") {
        id
        name
        language
      }
    }
    """
    response = graphql_client.post("/graphql", json={"query": mutation_refresh})
    result = response.json()
    assert "errors" not in result
    repo = result["data"]["refreshRepositories"]
    # Check that the returned repository object has the expected fields.
    assert repo is not None
    assert "id" in repo
    assert "name" in repo
    assert "language" in repo

    # Query repositories after refresh.
    query = "{ repositories { id name language } }"
    response = graphql_client.post("/graphql", json={"query": query})
    result = response.json()
    repos = result["data"]["repositories"]
    assert isinstance(repos, list)
    # Optionally, check that at least one repository was fetched.
    assert repos is not None


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

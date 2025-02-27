from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from sqlalchemy.pool import StaticPool
import os
import pytest
import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, User as ORMUser, OAuthCredential
from graphql_server.schemas.user_schema import User
from graphql_server.resolvers.user_resolver import UserQueryResolver
from graphql_server.resolvers.auth_resolver import AuthMutationResolver
from models.database import get_db
from graphql_server import schema
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI

# Use an in-memory SQLite database for tests.
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a single global test session.
global_test_session = TestingSessionLocal()

def override_get_db():
    # Always yield the same session.
    yield global_test_session


# Create all tables.
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fixture to clear the database before each test.
@pytest.fixture(autouse=True)
def clear_db():
    global_test_session.query(OAuthCredential).delete()
    global_test_session.query(ORMUser).delete()
    global_test_session.commit()
    yield
    global_test_session.query(OAuthCredential).delete()
    global_test_session.query(ORMUser).delete()
    global_test_session.commit()

# Create a base FastAPI app and override the get_db dependency.
app = FastAPI()
app.dependency_overrides[get_db] = override_get_db

# Default context getter for tests (without an authenticated user)
def test_context_getter():
    return {"db": next(override_get_db()), "user_id": None}

# Create the GraphQL router using the test context.
graphql_app = GraphQLRouter(schema, context_getter=test_context_getter)
app.include_router(graphql_app, prefix="/graphql")

client = TestClient(app)

def test_register():
    query = """
    mutation Register($input: RegisterInput!) {
        register(input: $input) {
            id
            username
            email
            isActive
        }
    }
    """
    variables = {
        "input": {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "TestPassword123"
        }
    }
    response = client.post("/graphql", json={"query": query, "variables": variables})
    data = response.json()
    assert "errors" not in data, f"Errors: {data.get('errors')}"
    user_data = data["data"]["register"]
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "testuser@example.com"
    assert user_data["isActive"] is True

def test_login():
    # Register a user first.
    query_reg = """
    mutation Register($input: RegisterInput!) {
        register(input: $input) {
            id
            username
            email
            isActive
        }
    }
    """
    variables_reg = {
        "input": {
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "TestPassword123"
        }
    }
    response_reg = client.post("/graphql", json={"query": query_reg, "variables": variables_reg})
    data_reg = response_reg.json()
    assert "errors" not in data_reg, f"Registration errors: {data_reg.get('errors')}"
    
    # Now perform login.
    query_login = """
    mutation Login($input: LoginInput!) {
        login(input: $input) {
            accessToken
            tokenType
        }
    }
    """
    variables_login = {
        "input": {
            "email": "loginuser@example.com",
            "password": "TestPassword123"
        }
    }
    response_login = client.post("/graphql", json={"query": query_login, "variables": variables_login})
    data_login = response_login.json()
    assert "errors" not in data_login, f"Login errors: {data_login.get('errors')}"
    token_data = data_login["data"]["login"]
    assert token_data["accessToken"] is not None
    assert token_data["tokenType"] == "bearer"

def test_me_unauthenticated():
    query = """
    {
        me {
            id
            username
            email
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    data = response.json()
    # Expect an error because no user is authenticated.
    assert "errors" in data, "Expected authentication error for 'me' query."

def test_me_authenticated():
    # Register a user to later simulate an authenticated request.
    query_reg = """
    mutation Register($input: RegisterInput!) {
        register(input: $input) {
            id
            username
            email
            isActive
        }
    }
    """
    variables_reg = {
        "input": {
            "username": "authuser",
            "email": "authuser@example.com",
            "password": "TestPassword123"
        }
    }
    response_reg = client.post("/graphql", json={"query": query_reg, "variables": variables_reg})
    data_reg = response_reg.json()
    user_id = int(data_reg["data"]["register"]["id"])

    users = global_test_session.query(ORMUser).all()

    def auth_context_getter():
        db = TestingSessionLocal()
        user = db.query(ORMUser).filter(ORMUser.id == user_id).first()
        # global_test_session.expire_all()
        return {"db": db, "user_id": user_id}

    # Create a temporary router with the authenticated context.
    auth_graphql_app = GraphQLRouter(schema, context_getter=auth_context_getter)
    app.include_router(auth_graphql_app, prefix="/auth-graphql")

    query_me = """
    {
        me {
            id
            username
            email
        }
    }
    """
    response = client.post("/auth-graphql", json={"query": query_me})
    data = response.json()
    assert "errors" not in data, f"Errors: {data.get('errors')}"
    me_data = data["data"]["me"]
    assert me_data["id"] == user_id
    assert me_data["username"] == "authuser"
    assert me_data["email"] == "authuser@example.com"


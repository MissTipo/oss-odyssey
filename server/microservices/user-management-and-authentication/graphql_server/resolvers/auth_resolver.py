import os
import datetime
import jwt
import strawberry
from fastapi import HTTPException
import requests
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from graphql_server.schemas.auth_schema import RegisterInput, LoginInput, Token
from graphql_server.schemas.user_schema import User as GraphQLUser
from models.models import User as ORMUser

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

def get_user_by_email(db: Session, email: str):
    return db.query(ORMUser).filter(ORMUser.email == email).first()

@strawberry.type
class AuthMutationResolver:
    @strawberry.mutation
    def register(self, info, input: RegisterInput) -> GraphQLUser:
        db: Session = info.context["db"]
        if get_user_by_email(db, input.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = pwd_context.hash(input.password)
        new_user = ORMUser(
            username=input.username,
            email=input.email,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return GraphQLUser(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
        )

    @strawberry.mutation
    def login(self, info, input: LoginInput) -> Token:
        db: Session = info.context["db"]
        user = get_user_by_email(db, input.email)
        if not user or not pwd_context.verify(input.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token_data = {"user_id": user.id, "email": user.email}
        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        return Token(access_token=access_token, token_type="bearer")

    @strawberry.mutation
    def githubAuth(self, info, code: str) -> Token:
        db: Session = info.context["db"]

        # Exchange the code for an access token
        token_url = "https://github.com/login/oauth/access_token"
        headers = {"Accept": "application/json"}
        data = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code
        }
        response = requests.post(token_url, headers=headers, data=data)
        token_data = response.json()

        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to authenticate with GitHub")

        access_token = token_data["access_token"]

        # Get GitHub user details
        user_url = "https://api.github.com/user"
        user_headers = {"Authorization": f"token {access_token}"}
        user_response = requests.get(user_url, headers=user_headers)
        github_user = user_response.json()

        if "email" not in github_user:
            raise HTTPException(status_code=400, detail="GitHub account has no public email")

        github_email = github_user["email"]
        github_username = github_user["login"]

        # Check if the user already exists
        user = db.query(ORMUser).filter(ORMUser.email == github_email).first()
        if not user:
            user = ORMUser(
                username=github_username,
                email=github_email,
                hashed_password=None,  # No password for GitHub users
                is_active=True,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate JWT token
        token_payload = {"user_id": user.id, "email": user.email}
        jwt_token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

        return Token(access_token=jwt_token, token_type="bearer")


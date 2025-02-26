import os
import datetime
import jwt
import strawberry
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from graphql_server.schemas.auth_schema import RegisterInput, LoginInput, Token
from graphql_server.schemas.user_schema import User as GraphQLUser
from models.user import User as ORMUser

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
        # In a real-world scenario, you would:
        #   1. Exchange the provided 'code' for an access token with GitHub.
        #   2. Use the access token to fetch the GitHub user's email and username.
        #   3. Create or update the user in your database.
        # For this example, we'll simulate a GitHub user:
        github_email = "githubuser@example.com"
        github_username = "githubuser"
        
        user = db.query(ORMUser).filter(ORMUser.email == github_email).first()
        if not user:
            # Register new GitHub user (you might handle this differently)
            user = ORMUser(
                username=github_username,
                email=github_email,
                hashed_password=pwd_context.hash("default_password"),  # Placeholder; consider better handling.
                is_active=True,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        token_data = {"user_id": user.id, "email": user.email}
        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        return Token(access_token=access_token, token_type="bearer")


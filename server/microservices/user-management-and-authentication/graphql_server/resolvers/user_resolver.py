import strawberry
from sqlalchemy.orm import Session
from fastapi import HTTPException
from graphql_server.schemas.user_schema import User as GraphQLUser, UpdateUserInput
from models.models import User as ORMUser
import datetime
from typing import List

@strawberry.type
class UserQueryResolver:
    @strawberry.field
    def me(self, info) -> GraphQLUser:
        db: Session = info.context["db"]
        user_id = info.context.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = db.query(ORMUser).filter(ORMUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return GraphQLUser(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    @strawberry.field
    def all_users(self, info) -> List[GraphQLUser]:
        db: Session = info.context["db"]
        users = db.query(ORMUser).all()
        return [
            GraphQLUser(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users
        ]

@strawberry.type
class UserMutationResolver:
    @strawberry.mutation
    def updateUser(self, info, input: UpdateUserInput) -> GraphQLUser:
        db: Session = info.context["db"]
        user = db.query(ORMUser).filter(ORMUser.id == input.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if input.username is not None:
            user.username = input.username
        if input.email is not None:
            user.email = input.email
        if input.is_active is not None:
            user.is_active = input.is_active
        
        user.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return GraphQLUser(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @strawberry.mutation
    def deleteUser(self, info, id: int) -> GraphQLUser:
        db: Session = info.context["db"]
        user = db.query(ORMUser).filter(ORMUser.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Capture user details before deletion (optional)
        deleted_user = GraphQLUser(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        db.delete(user)
        db.commit()
        
        return deleted_user



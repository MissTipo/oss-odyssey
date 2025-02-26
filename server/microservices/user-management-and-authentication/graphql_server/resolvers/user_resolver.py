import strawberry
from sqlalchemy.orm import Session
from fastapi import HTTPException
from graphql_server.schemas.user_schema import User as GraphQLUser
from models.user import User as ORMUser

@strawberry.type
class UserQueryResolver:
    @strawberry.field
    def me(self, info) -> GraphQLUser:
        db: Session = info.context["db"]
        # Assumes your authentication middleware injects 'user_id' into context
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


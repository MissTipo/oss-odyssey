from fastapi import Request
from models.database import SessionLocal

async def get_context(request: Request):
    # Create a new database session
    db = SessionLocal()
    # Optionally, extract user_id from the request if available
    # For example, if you've set it somewhere in middleware:
    user_id = getattr(request.state, "user_id", None)
    return {"request": request, "db": db, "user_id": user_id}

import strawberry
from strawberry.fastapi import GraphQLRouter
from graphql_server.schemas.user_schema import User
from graphql_server.schemas.auth_schema import Token, RegisterInput, LoginInput
from graphql_server.resolvers.user_resolver import UserQueryResolver, UserMutationResolver
from graphql_server.resolvers.auth_resolver import AuthMutationResolver
from fastapi import Depends

# Instantiate resolver classes
user_query_resolver = UserQueryResolver()
auth_mutation_resolver = AuthMutationResolver()
user_mutation_resolver = UserMutationResolver()

@strawberry.type
class Query:
    me: User = strawberry.field(resolver=UserQueryResolver.me)
    all_users: list[User] = strawberry.mutation(resolver=UserQueryResolver.all_users)

@strawberry.type
class Mutation:
    register: User = strawberry.mutation(resolver=AuthMutationResolver.register)
    login: Token = strawberry.mutation(resolver=AuthMutationResolver.login)
    github_auth: Token = strawberry.mutation(resolver=AuthMutationResolver.githubAuth)
    update_user: User = strawberry.mutation(resolver=UserMutationResolver.updateUser)
    delete_user: User = strawberry.mutation(resolver=UserMutationResolver.deleteUser)

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

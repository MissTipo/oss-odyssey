# graphql_server/__init__.py
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import Request
from models.database import SessionLocal
from graphql_server.schemas.bookmark_schema import Bookmark
from graphql_server.resolvers.bookmark_resolver import BookmarkQueryResolver, BookmarkMutationResolver

async def get_context(request: Request):
    db = SessionLocal()
    user_id = getattr(request.state, "user_id", None)  # Set by auth middleware
    return {"request": request, "db": db, "user_id": user_id}

@strawberry.type
class Query:
    get_bookmarks: list[Bookmark] = strawberry.field(resolver=BookmarkQueryResolver.get_bookmarks)

@strawberry.type
class Mutation:
    create_bookmark: Bookmark = strawberry.mutation(resolver=BookmarkMutationResolver.create_bookmark)
    update_bookmark: Bookmark = strawberry.mutation(resolver=BookmarkMutationResolver.update_bookmark)
    delete_bookmark: Bookmark = strawberry.mutation(resolver=BookmarkMutationResolver.delete_bookmark)

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)


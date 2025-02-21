from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List
from .schemas.issue_schema import Issue
from .resolvers.issue_resolver import QueryResolver, MutationResolver
from models.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

def get_context(db: Session = Depends(get_db)):
    return {"db": db}

@strawberry.type
class Query:
    issues: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues)
    issue: Issue = strawberry.field(resolver=QueryResolver.get_issue_by_id)
    issues_by_state: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues_by_state)
    issues_by_source: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues_by_source)
    issues_by_label: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues_by_label)

@strawberry.type
class Mutation:
    refresh_issues: str = strawberry.mutation(resolver=MutationResolver.refreshIssues)
    """create_issue: Issue = strawberry.field(resolver=MutationResolver.create_issue)
    update_issue: Issue = strawberry.field(resolver=MutationResolver.update_issue)
    delete_issue: Issue = strawberry.field(resolver=MutationResolver.delete_issue)"""

# Add the context to the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

from strawberry.fastapi import GraphQLRouter

import strawberry
from typing import List, Union
from .schemas.issue_schema import Issue
from .resolvers.issue_resolver import QueryResolver, MutationResolver

@strawberry.type
class Query:
    issues: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues)
    issue: Issue = strawberry.field(resolver=QueryResolver.get_issue)

@strawberry.type
class Mutation:
    create_issue: Issue = strawberry.field(resolver=MutationResolver.create_issue)
    update_issue: Issue = strawberry.field(resolver=MutationResolver.update_issue)
    delete_issue: Issue = strawberry.field(resolver=MutationResolver.delete_issue)




schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

import strawberry
from graphql_server.schemas.user_schema import User
from graphql_server.schemas.auth_schema import Token, RegisterInput, LoginInput
from graphql_server.resolvers.user_resolver import UserQueryResolver
from graphql_server.resolvers.auth_resolver import AuthMutationResolver

@strawberry.type
class Query:
    me: User = strawberry.field(resolver=UserQueryResolver.me)

@strawberry.type
class Mutation:
    register: User = strawberry.mutation(resolver=AuthMutationResolver.register)
    login: Token = strawberry.mutation(resolver=AuthMutationResolver.login)
    github_auth: Token = strawberry.mutation(resolver=AuthMutationResolver.githubAuth)

schema = strawberry.Schema(query=Query, mutation=Mutation)


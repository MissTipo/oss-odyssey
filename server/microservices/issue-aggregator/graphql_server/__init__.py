from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List
from .schemas.issue_schema import Issue
from .schemas.label_schema import Label
from .schemas.project_schema import Project
from .schemas.repo_schema import Repository
from .schemas.user_issue_schema import UserIssue
from .schemas.issue_label_schema import IssueLabelAssociation
from .resolvers.issue_resolver import QueryResolver, MutationResolver
from .resolvers.label_resolver import LabelQueryResolver, LabelMutationResolver
from .resolvers.project_resolver import ProjectQueryResolver, ProjectMutationResolver
from .resolvers.repo_resolver import RepoQueryResolver, RepoMutationResolver
from .resolvers.user_issue_resolver import UserIssueQueryResolver, UserIssueMutationResolver
from .resolvers.issue_label_resolver import IssueLabelQueryResolver, IssueLabelMutationResolver
from models.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

def get_context(db: Session = Depends(get_db)):
    return {"db": db}

@strawberry.type
class Query:
    # Issue queries
    issues: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues)
    issue: Issue = strawberry.field(resolver=QueryResolver.get_issue_by_id)
    issues_by_state: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues_by_state)
    issues_by_source: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues_by_source)
    issues_by_label: List[Issue] = strawberry.field(resolver=QueryResolver.get_issues_by_label)

    # Label queries
    labels: List[Label] = strawberry.field(resolver=LabelQueryResolver.get_labels)
    label: Label = strawberry.field(resolver=LabelQueryResolver.get_label_by_id)
    labels_by_repository: List[Label] = strawberry.field(resolver=LabelQueryResolver.get_labels_by_repository)

    # Repository queries
    repositories: List[Repository] = strawberry.field(resolver=RepoQueryResolver.get_repositories)
    repository: Repository = strawberry.field(resolver=RepoQueryResolver.get_repository_by_id)
    repositories_by_source: List[Repository] = strawberry.field(resolver=RepoQueryResolver.get_repositories_by_source)

    # Project queries
    projects: List[Project] = strawberry.field(resolver=ProjectQueryResolver.get_projects)
    project: Project = strawberry.field(resolver=ProjectQueryResolver.get_project_by_id)
    projects_by_owner: List[Project] = strawberry.field(resolver=ProjectQueryResolver.get_projects_by_owner)

    # UserIssue queries
    user_issues: List[UserIssue] = strawberry.field(resolver=UserIssueQueryResolver.get_user_issues)
    user_issue: UserIssue = strawberry.field(resolver=UserIssueQueryResolver.get_user_issue_by_id)
    user_issues_by_project: List[UserIssue] = strawberry.field(resolver=UserIssueQueryResolver.get_user_issues_by_project)

    # IssueLabel queries
    issue_label_associations: List[IssueLabelAssociation] = strawberry.field(resolver=IssueLabelQueryResolver.get_issue_label_associations)
    issue_label_association: IssueLabelAssociation = strawberry.field(resolver=IssueLabelQueryResolver.get_issue_label_association_by_id)
    labels_for_issue: List[IssueLabelAssociation] = strawberry.field(resolver=IssueLabelQueryResolver.get_labels_by_issue)
    issues_for_label: List[IssueLabelAssociation] = strawberry.field(resolver=IssueLabelQueryResolver.get_issues_by_label)

@strawberry.type
class Mutation:
    # Issue mutations
    refresh_issues: str = strawberry.mutation(resolver=MutationResolver.refreshIssues)
    """create_issue: Issue = strawberry.field(resolver=MutationResolver.create_issue)
    update_issue: Issue = strawberry.field(resolver=MutationResolver.update_issue)
    delete_issue: Issue = strawberry.field(resolver=MutationResolver.delete_issue)"""

    # Label mutations
    createLabel: Label = strawberry.mutation(resolver=LabelMutationResolver.createLabel)
    updateLabel: Label = strawberry.mutation(resolver=LabelMutationResolver.updateLabel)
    deleteLabel: str = strawberry.mutation(resolver=LabelMutationResolver.deleteLabel)

    # Repository mutations
    createRepository: Repository = strawberry.mutation(resolver=RepoMutationResolver.createRepository)
    updateRepository: Repository = strawberry.mutation(resolver=RepoMutationResolver.updateRepository)
    deleteRepository: str = strawberry.mutation(resolver=RepoMutationResolver.deleteRepository)

    # Project mutations
    createProject: Project = strawberry.mutation(resolver=ProjectMutationResolver.createProject)
    updateProject: Project = strawberry.mutation(resolver=ProjectMutationResolver.updateProject)
    deleteProject: str = strawberry.mutation(resolver=ProjectMutationResolver.deleteProject)

    # UserIssue mutations
    createUserIssue: UserIssue = strawberry.mutation(resolver=UserIssueMutationResolver.createUserIssue)
    updateUserIssue: UserIssue = strawberry.mutation(resolver=UserIssueMutationResolver.updateUserIssue)
    deleteUserIssue: str = strawberry.mutation(resolver=UserIssueMutationResolver.deleteUserIssue)

    # IssueLabel mutations
    createIssueLabelAssociation: IssueLabelAssociation = strawberry.mutation(resolver=IssueLabelMutationResolver.createIssueLabelAssociation)
    deleteIssueLabelAssociation: str = strawberry.mutation(resolver=IssueLabelMutationResolver.deleteIssueLabelAssociation)

# Add the context to the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

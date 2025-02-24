"""
user_issue_resolver.py

Resolver for managing user-specific issues within a project.
Handles READ operations via QueryResolver and WRITE operations via MutationResolver.
"""

import datetime
import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from graphql_server.schemas.user_issue_schema import UserIssue, Status
from models.models import UserIssues
from integrations.github_integration import fetch_github_issues
from integrations.gitlab_integration import fetch_gitlab_issues


def map_user_issue(orm_user_issue: UserIssues) -> UserIssue:
    """
    Maps an ORM user issue instance to the GraphQL UserIssue type.
    """
    status_enum = Status(orm_user_issue.status)
    return UserIssue(
        issue_id=orm_user_issue.id,
        issue=orm_user_issue.issue,
        project_id=orm_user_issue.project_id,
        status=status_enum,
        pr_link=orm_user_issue.pr_link,
        created_at=orm_user_issue.created_at,
        updated_at=orm_user_issue.updated_at,
    )


class UserIssueQueryResolver:
    @staticmethod
    def get_user_issues(info) -> List[UserIssue]:
        """
        Retrieves all user issues from the database.
        """
        db: Session = info.context["db"]
        orm_user_issues = db.query(UserIssues).all()
        return [map_user_issue(ui) for ui in orm_user_issues]

    @staticmethod
    def get_user_issue_by_id(info, issue_id: int) -> Optional[UserIssue]:
        """
        Retrieves a single user issue by its unique identifier.
        """
        db: Session = info.context["db"]
        orm_user_issue = db.query(UserIssues).filter(UserIssues.id == issue_id).first()
        return map_user_issue(orm_user_issue) if orm_user_issue else None

    @staticmethod
    def get_user_issues_by_project(info, project_id: int) -> List[UserIssue]:
        """
        Retrieves all user issues associated with a specific project.
        """
        db: Session = info.context["db"]
        orm_user_issues = db.query(UserIssues).filter(UserIssues.project_id == project_id).all()
        return [map_user_issue(ui) for ui in orm_user_issues]


@strawberry.type
class UserIssueMutationResolver:
    @strawberry.mutation
    def createUserIssue(
        self,
        info,
        issue: int,
        project_id: int,
        status: Status,
        pr_link: str
    ) -> UserIssue:
        """
        Creates a new user issue in the database.
        """
        db: Session = info.context["db"]
        now = datetime.datetime.utcnow()
        new_user_issue = UserIssues(
            issue=issue,
            project_id=project_id,
            status=status.value,
            pr_link=pr_link,
            created_at=now,
            updated_at=now,
        )
        db.add(new_user_issue)
        db.commit()
        db.refresh(new_user_issue)
        return map_user_issue(new_user_issue)

    @strawberry.mutation
    def updateUserIssue(
        self,
        info,
        issue_id: int,
        issue: Optional[int] = None,
        project_id: Optional[int] = None,
        status: Optional[Status] = None,
        pr_link: Optional[str] = None
    ) -> UserIssue:
        """
        Updates an existing user issue.
        """
        db: Session = info.context["db"]
        user_issue = db.query(UserIssues).filter(UserIssues.id == issue_id).first()
        if not user_issue:
            raise Exception(f"User issue with id {issue_id} not found")
        if issue is not None:
            user_issue.issue = issue
        if project_id is not None:
            user_issue.project_id = project_id
        if status is not None:
            user_issue.status = status.value
        if pr_link is not None:
            user_issue.pr_link = pr_link
        user_issue.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(user_issue)
        return map_user_issue(user_issue)

    @strawberry.mutation
    def deleteUserIssue(self, info, issue_id: int) -> str:
        """
        Deletes a user issue from the database.
        """
        db: Session = info.context["db"]
        user_issue = db.query(UserIssues).filter(UserIssues.id == issue_id).first()
        if not user_issue:
            raise Exception(f"User issue with id {issue_id} not found")
        db.delete(user_issue)
        db.commit()
        return f"User issue with id {issue_id} deleted successfully"


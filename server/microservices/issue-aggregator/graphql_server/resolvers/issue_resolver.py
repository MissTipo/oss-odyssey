
"""
Resolver for retrieving issue data from the database.
The QueryResolver handles the READ operations/retrieving data from the database.
The MutationResolver handles the write operations or CREATE, UPDATE, DELETE operations.
"""

import datetime
from typing import List, Optional, Union
from strawberry import ID
from graphql_server.schemas.issue_schema import Issue as GraphQLIssue, State, Source
from models.models import Issues
from sqlalchemy.orm import Session

def map_issue(orm_issue: Issues) -> GraphQLIssue:
    # Convert the boolean state to a GraphQL enum value.
    state_enum = State.OPEN if orm_issue.state else State.CLOSED

    # For the source, ensure the string matches the enum values (assuming lowercase)
    if orm_issue.source:
        source_enum = Source(orm_issue.source.lower())
    else:
        source_enum = None

    return GraphQLIssue(
        id=orm_issue.id,
        external_id=getattr(orm_issue, "external_id", None),  # adjust if needed
        title=orm_issue.title,
        description=orm_issue.description,
        state=state_enum,
        created_at=getattr(orm_issue, "created_at", datetime.datetime.utcnow()),
        updated_at=getattr(orm_issue, "updated_at", datetime.datetime.utcnow()),
        url=getattr(orm_issue, "url", ""),
        source=source_enum,
        labels=getattr(orm_issue, "labels", []),
        repository_id=getattr(orm_issue, "repository_id", 0)
    )

class QueryResolver:
    @staticmethod
    def get_issues(info) -> List[GraphQLIssue]:
        db: Session = info.context["db"]
        orm_issues = db.query(Issues).all()
        # Map each ORM object to the GraphQL type.
        return [map_issue(issue) for issue in orm_issues]

    @staticmethod
    def get_issue_by_id(info, id: int) -> Optional[GraphQLIssue]:
        db: Session = info.context["db"]
        orm_issue = db.query(Issues).filter(Issues.id == id).first()
        return map_issue(orm_issue) if orm_issue else None

    @staticmethod
    def get_issues_by_state(info, state: State) -> List[GraphQLIssue]:
        db: Session = info.context["db"]
        # Assuming your ORM stores state as a boolean: True for OPEN, False for CLOSED.
        orm_issues = db.query(Issues).filter(Issues.state == (state == State.OPEN)).all()
        return [map_issue(issue) for issue in orm_issues]

    @staticmethod
    def get_issues_by_source(info, source: Source) -> List[GraphQLIssue]:
        db: Session = info.context["db"]
        # If the ORM model stores source as a lowercase string.
        orm_issues = db.query(Issues).filter(Issues.source == source.value).all()
        return [map_issue(issue) for issue in orm_issues]

    @staticmethod
    def get_issues_by_label(info, label: str) -> List[GraphQLIssue]:
        db: Session = info.context["db"]
        orm_issues = db.query(Issues).filter(Issues.labels.contains(label)).all()
        return [map_issue(issue) for issue in orm_issues]


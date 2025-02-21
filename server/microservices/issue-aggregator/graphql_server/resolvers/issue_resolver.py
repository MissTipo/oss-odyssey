
"""
Resolver for retrieving issue data from the database.
The QueryResolver handles the READ operations/retrieving data from the database.
The MutationResolver handles the write operations or CREATE, UPDATE, DELETE operations.
"""

import datetime
import strawberry
from typing import List, Optional, Union
from strawberry import ID
from graphql_server.schemas.issue_schema import Issue as GraphQLIssue, State, Source
from models.models import Issues
from sqlalchemy.orm import Session
from integrations.github_integration import fetch_github_issues
from integrations.gitlab_integration import fetch_gitlab_issues

def map_issue(orm_issue: Issues) -> GraphQLIssue:
    # Convert the boolean state to a GraphQL enum value.
    state_enum = State.OPEN if orm_issue.state else State.CLOSED

    # convert to the proper enum (assuming lowercase for GraphQL)
    source_enum = Source(orm_issue.source.lower()) if orm_issue.source else None

    # Ensure labels is an iterable of strings:
    raw_labels = getattr(orm_issue, "labels", None)
    if raw_labels is None or raw_labels == "":
        labels_list = []
    elif isinstance(raw_labels, list):
        labels_list = [str(label) for label in raw_labels]
    elif isinstance(raw_labels, str):
        # Load as JSON; if that fails, assume it's comma-separated.
        try:
            parsed = json.loads(raw_labels)
            if isinstance(parsed, list):
                labels_list = [str(label) for label in parsed]
            else:
                labels_list = [str(parsed)]
        except Exception:
            labels_list = [_label.strip() for _label in raw_labels.split(",") if _label.strip()]
    else:
        labels_list = []


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
        labels=labels_list,
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
        # ORM stores state as a boolean: True for OPEN, False for CLOSED.
        orm_issues = db.query(Issues).filter(Issues.state == (state == State.OPEN)).all()
        return [map_issue(issue) for issue in orm_issues]

    @staticmethod
    def get_issues_by_source(info, source: Source) -> List[GraphQLIssue]:
        db: Session = info.context["db"]
        orm_issues = db.query(Issues).filter(Issues.source == source.value).all()
        return [map_issue(issue) for issue in orm_issues]

    @staticmethod
    def get_issues_by_label(info, label: str) -> List[GraphQLIssue]:
        db: Session = info.context["db"]
        orm_issues = db.query(Issues).filter(Issues.labels.contains(label)).all()
        return [map_issue(issue) for issue in orm_issues]

@strawberry.type
class MutationResolver:
    @strawberry.mutation
    def refreshIssues(self, info) -> str:
        db: Session = info.context["db"]
        try:
            # Delete existing issues.
            db.query(Issues).delete()
            db.commit()
            
            # Fetch issues from GitHub.
            data = fetch_github_issues("apache", "airflow", "good first issue")
            # print("GitHub response:", data)
            new_issues = []
            
            # Process the data returned from GitHub.
            for edge in data.get("data", {}).get("repository", {}).get("issues", {}).get("edges", []):
                node = edge["node"]
                # Create a new ORM object from the node data.
                new_issue = Issues(
                    external_id=node["number"],
                    title=node["title"],
                    description=node["body"][:150],
                    state=True,  # True means OPEN
                    created_at=datetime.datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00")),
                    updated_at=datetime.datetime.fromisoformat(node["updatedAt"].replace("Z", "+00:00")),
                    url=node["url"],
                    source="github",
                    labels=[lbl["name"] for lbl in node.get("labels", {}).get("nodes", [])],
                    repository_id=0  # To be adjusted based on needs.
                )
                db.add(new_issue)
                new_issues.append(new_issue)
            
            db.commit()  # Commit all new issues to the database.
            return "Issues refreshed successfully"
        except Exception as e:
            db.rollback()
            return f"Failed to refresh issues: {str(e)}"


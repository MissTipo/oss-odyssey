"""
label_resolver.py

Resolver for retrieving and modifying label data from the database.
Handles READ operations (via QueryResolver) and WRITE operations (via MutationResolver).
"""

import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from graphql_server.schemas.label_schema import Label as GraphQLLabel
from models.models import Labels
from integrations.github_integration import fetch_github_issues, fetch_github_labels
from integrations.gitlab_integration import fetch_gitlab_issues


def map_label(orm_label: Labels) -> GraphQLLabel:
    """
    Maps an ORM label instance to the GraphQL Label type.
    """
    return GraphQLLabel(
        label_id=orm_label.id,
        name=orm_label.name,
        color=orm_label.color,
        description=orm_label.description,
        repository_id=orm_label.repository_id,
    )


class LabelQueryResolver:
    @staticmethod
    def get_labels(info) -> List[GraphQLLabel]:
        """
        Retrieves all labels from the database.
        """
        db: Session = info.context["db"]
        orm_labels = db.query(Labels).all()
        return [map_label(label) for label in orm_labels]

    @staticmethod
    def get_label_by_id(info, label_id: int) -> Optional[GraphQLLabel]:
        """
        Retrieves a label by its unique identifier.
        """
        db: Session = info.context["db"]
        orm_label = db.query(Labels).filter(Labels.id == label_id).first()
        return map_label(orm_label) if orm_label else None

    @staticmethod
    def get_labels_by_repository(info, repository_id: int) -> List[GraphQLLabel]:
        """
        Retrieves all labels associated with a specific repository.
        """
        db: Session = info.context["db"]
        orm_labels = db.query(Labels).filter(Labels.repository_id == repository_id).all()
        return [map_label(label) for label in orm_labels]


@strawberry.type
class LabelMutationResolver:
    @strawberry.mutation
    def refreshLabels(self, info, repository_owner: str, repository_name: str) -> str:
        db: Session = info.context["db"]
        try:
            # Fetch labels from GitHub.
            data = fetch_github_labels(repository_owner, repository_name)
            # Clear existing labels.
            db.query(Labels).delete()
            for label in data:
                new_label = Labels(
                    name=label.get("name", ""),
                    color=label.get("color", "#000000"),
                    description=label.get("description", ""),
                    repository_id=0  # Adjust if needed.
                )
                db.add(new_label)
            db.commit()
            return "Labels refreshed successfully"
        except Exception as e:
            db.rollback()
            return f"Failed to refresh labels: {str(e)}"


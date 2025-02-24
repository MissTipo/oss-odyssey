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
from integrations.github_integration import fetch_github_issues
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
    def createLabel(
        self, info, name: str, color: str, description: str, repository_id: int
    ) -> GraphQLLabel:
        """
        Creates a new label in the database.
        """
        db: Session = info.context["db"]
        new_label = Labels(
            name=name,
            color=color,
            description=description,
            repository_id=repository_id,
        )
        db.add(new_label)
        db.commit()
        db.refresh(new_label)
        return map_label(new_label)

    @strawberry.mutation
    def updateLabel(
        self,
        info,
        label_id: int,
        name: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
        repository_id: Optional[int] = None,
    ) -> GraphQLLabel:
        """
        Updates an existing label.
        """
        db: Session = info.context["db"]
        label = db.query(Labels).filter(Labels.id == label_id).first()
        if not label:
            raise Exception(f"Label with id {label_id} not found")
        if name is not None:
            label.name = name
        if color is not None:
            label.color = color
        if description is not None:
            label.description = description
        if repository_id is not None:
            label.repository_id = repository_id
        db.commit()
        db.refresh(label)
        return map_label(label)

    @strawberry.mutation
    def deleteLabel(self, info, label_id: int) -> str:
        """
        Deletes a label from the database.
        """
        db: Session = info.context["db"]
        label = db.query(Labels).filter(Labels.id == label_id).first()
        if not label:
            raise Exception(f"Label with id {label_id} not found")
        db.delete(label)
        db.commit()
        return f"Label with id {label_id} deleted successfully"


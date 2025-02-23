"""
issue_label_resolver.py

Resolver for managing the many-to-many relationship between issues and labels.
Handles READ operations via QueryResolver and WRITE operations via MutationResolver.
"""

import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from graphql_server.schemas.issue_label_schema import IssueLabelAssociation
from models.models import IssueLabel  # Assumes your ORM model is named "IssueLabel"


def map_issue_label(orm_issue_label: IssueLabel) -> IssueLabelAssociation:
    """
    Maps an ORM IssueLabel instance to the GraphQL IssueLabelAssociation type.
    """
    return IssueLabelAssociation(
        id=orm_issue_label.id,
        issue_id=orm_issue_label.issue_id,
        label_id=orm_issue_label.label_id,
    )


class QueryResolver:
    @staticmethod
    def get_issue_label_associations(info) -> List[IssueLabelAssociation]:
        """
        Retrieves all issue-label associations from the database.
        """
        db: Session = info.context["db"]
        orm_issue_labels = db.query(IssueLabel).all()
        return [map_issue_label(association) for association in orm_issue_labels]

    @staticmethod
    def get_issue_label_association_by_id(info, id: int) -> Optional[IssueLabelAssociation]:
        """
        Retrieves a single issue-label association by its unique identifier.
        """
        db: Session = info.context["db"]
        orm_issue_label = db.query(IssueLabel).filter(IssueLabel.id == id).first()
        return map_issue_label(orm_issue_label) if orm_issue_label else None

    @staticmethod
    def get_labels_by_issue(info, issue_id: int) -> List[IssueLabelAssociation]:
        """
        Retrieves all label associations for a specific issue.
        """
        db: Session = info.context["db"]
        orm_issue_labels = db.query(IssueLabel).filter(IssueLabel.issue_id == issue_id).all()
        return [map_issue_label(association) for association in orm_issue_labels]

    @staticmethod
    def get_issues_by_label(info, label_id: int) -> List[IssueLabelAssociation]:
        """
        Retrieves all issue associations for a specific label.
        """
        db: Session = info.context["db"]
        orm_issue_labels = db.query(IssueLabel).filter(IssueLabel.label_id == label_id).all()
        return [map_issue_label(association) for association in orm_issue_labels]


@strawberry.type
class MutationResolver:
    @strawberry.mutation
    def createIssueLabelAssociation(
        self, info, issue_id: int, label_id: int
    ) -> IssueLabelAssociation:
        """
        Creates a new issue-label association in the database.
        """
        db: Session = info.context["db"]
        new_association = IssueLabel(
            issue_id=issue_id,
            label_id=label_id,
        )
        db.add(new_association)
        db.commit()
        db.refresh(new_association)
        return map_issue_label(new_association)

    @strawberry.mutation
    def deleteIssueLabelAssociation(self, info, id: int) -> str:
        """
        Deletes an existing issue-label association from the database.
        """
        db: Session = info.context["db"]
        association = db.query(IssueLabel).filter(IssueLabel.id == id).first()
        if not association:
            raise Exception(f"IssueLabel association with id {id} not found")
        db.delete(association)
        db.commit()
        return f"IssueLabel association with id {id} deleted successfully"


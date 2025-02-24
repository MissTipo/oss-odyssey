"""
repo_resolver.py

Resolver for retrieving and modifying repository data from the database.
Handles READ operations via QueryResolver and WRITE operations via MutationResolver.
"""

import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from graphql_server.schemas.repo_schema import Repository, Source
from models.models import Repositories
from integrations.github_integration import fetch_github_issues
from integrations.gitlab_integration import fetch_gitlab_issues


def map_repository(orm_repo: Repositories) -> Repository:
    """
    Maps an ORM repository instance to the GraphQL Repository type.
    """
    # Convert the source string (e.g., "github") to the corresponding GraphQL enum.
    source_enum = Source(orm_repo.source.lower()) if orm_repo.source else None

    return Repository(
        id=orm_repo.id,
        external_id=orm_repo.external_id,
        name=orm_repo.name,
        full_name=orm_repo.full_name,
        description=orm_repo.description,
        url=orm_repo.url,
        source=source_enum,
    )


class RepoQueryResolver:
    @staticmethod
    def get_repositories(info) -> List[Repository]:
        """
        Retrieves all repositories from the database.
        """
        db: Session = info.context["db"]
        orm_repos = db.query(Repositories).all()
        return [map_repository(repo) for repo in orm_repos]

    @staticmethod
    def get_repository_by_id(info, id: int) -> Optional[Repository]:
        """
        Retrieves a single repository by its unique identifier.
        """
        db: Session = info.context["db"]
        orm_repo = db.query(Repositories).filter(Repositories.id == id).first()
        return map_repository(orm_repo) if orm_repo else None

    @staticmethod
    def get_repositories_by_source(info, source: Source) -> List[Repository]:
        """
        Retrieves repositories filtered by source (GitHub or GitLab).
        """
        db: Session = info.context["db"]
        orm_repos = db.query(Repositories).filter(Repositories.source == source.value).all()
        return [map_repository(repo) for repo in orm_repos]


@strawberry.type
class RepoMutationResolver:
    @strawberry.mutation
    def createRepository(
        self, info, external_id: str, name: str, full_name: str,
        description: str, url: str, source: Source
    ) -> Repository:
        """
        Creates a new repository in the database.
        """
        db: Session = info.context["db"]
        new_repo = Repositories(
            external_id=external_id,
            name=name,
            full_name=full_name,
            description=description,
            url=url,
            source=source.value
        )
        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)
        return map_repository(new_repo)

    @strawberry.mutation
    def updateRepository(
        self, info, id: int,
        external_id: Optional[str] = None,
        name: Optional[str] = None,
        full_name: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        source: Optional[Source] = None,
    ) -> Repository:
        """
        Updates an existing repository.
        """
        db: Session = info.context["db"]
        repo = db.query(Repositories).filter(Repositories.id == id).first()
        if not repo:
            raise Exception(f"Repository with id {id} not found")
        if external_id is not None:
            repo.external_id = external_id
        if name is not None:
            repo.name = name
        if full_name is not None:
            repo.full_name = full_name
        if description is not None:
            repo.description = description
        if url is not None:
            repo.url = url
        if source is not None:
            repo.source = source.value
        db.commit()
        db.refresh(repo)
        return map_repository(repo)

    @strawberry.mutation
    def deleteRepository(self, info, id: int) -> str:
        """
        Deletes a repository from the database.
        """
        db: Session = info.context["db"]
        repo = db.query(Repositories).filter(Repositories.id == id).first()
        if not repo:
            raise Exception(f"Repository with id {id} not found")
        db.delete(repo)
        db.commit()
        return f"Repository with id {id} deleted successfully"


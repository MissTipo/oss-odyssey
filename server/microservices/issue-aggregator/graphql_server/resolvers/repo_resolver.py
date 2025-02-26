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
from integrations.github_integration import fetch_github_issues, fetch_github_repositories
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
        language=orm_repo.language,
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

    @staticmethod
    def get_repositories_by_label(info, label: str) -> List[Repository]:
        # For remote fetching based on label.
        data = fetch_github_repositories(label=label)
        repos = []
        for repo in data:
            repos.append(Repository(
                id=repo.get("id", 0),
                external_id=repo.get("external_id", ""),
                name=repo.get("name", ""),
                full_name=repo.get("full_name", ""),
                description=repo.get("description", ""),
                url=repo.get("url", ""),
                source=Source.GITHUB,
                language=orm_repo.language,
                # language=repo.get("language", "")
            ))
        return repos


@strawberry.type
class RepoMutationResolver:
    @strawberry.mutation
    def refreshRepositories(self, info, label: str) -> Repository:
        db: Session = info.context["db"]
        try:
            data = fetch_github_repositories(label=label)
            # Clear current repositories.
            db.query(Repositories).delete()
            last_repo = None
            for repo_data in data:
                new_repo = Repositories(
                    external_id=repo_data.get("external_id", ""),
                    name=repo_data.get("name", ""),
                    full_name=repo_data.get("full_name", ""),
                    description=repo_data.get("description", ""),
                    url=repo_data.get("url", ""),
                    source="github",
                    # language=repo_data.get("language", "")
                    language= ""
                )
                db.add(new_repo)
                last_repo = new_repo
            db.commit()
            if last_repo is None:
                raise Exception("No repositories fetched")
            return map_repository(last_repo)  # Use your mapping function to convert ORM to GraphQL type.
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to refresh repositories: {str(e)}")


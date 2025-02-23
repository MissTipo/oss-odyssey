"""
project_resolver.py

Resolver for retrieving and modifying project data from the database.
Handles READ operations via QueryResolver and WRITE operations via MutationResolver.
"""

import datetime
import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from graphql_server.schemas.project_schema import Project, Source
from models.models import Projects  # Assumes your ORM model for projects is named "Projects"


def map_project(orm_project: Projects) -> Project:
    """
    Maps an ORM project instance to the GraphQL Project type.
    """
    source_enum = Source(orm_project.source.lower()) if orm_project.source else None
    return Project(
        project_id=orm_project.id,
        name=orm_project.name,
        description=orm_project.description,
        url=orm_project.url,
        source=source_enum,
        repository_id=orm_project.repository_id,
        owner_id=orm_project.owner_id,
        created_at=orm_project.created_at,
        updated_at=orm_project.updated_at,
    )


class QueryResolver:
    @staticmethod
    def get_projects(info) -> List[Project]:
        """
        Retrieves all projects from the database.
        """
        db: Session = info.context["db"]
        orm_projects = db.query(Projects).all()
        return [map_project(project) for project in orm_projects]

    @staticmethod
    def get_project_by_id(info, project_id: int) -> Optional[Project]:
        """
        Retrieves a single project by its unique identifier.
        """
        db: Session = info.context["db"]
        orm_project = db.query(Projects).filter(Projects.id == project_id).first()
        return map_project(orm_project) if orm_project else None

    @staticmethod
    def get_projects_by_owner(info, owner_id: int) -> List[Project]:
        """
        Retrieves projects created by a specific owner.
        """
        db: Session = info.context["db"]
        orm_projects = db.query(Projects).filter(Projects.owner_id == owner_id).all()
        return [map_project(project) for project in orm_projects]


@strawberry.type
class MutationResolver:
    @strawberry.mutation
    def createProject(
        self,
        info,
        name: str,
        description: str,
        url: str,
        source: Source,
        repository_id: int,
        owner_id: int,
    ) -> Project:
        """
        Creates a new project in the database.
        """
        db: Session = info.context["db"]
        now = datetime.datetime.utcnow()
        new_project = Projects(
            name=name,
            description=description,
            url=url,
            source=source.value,
            repository_id=repository_id,
            owner_id=owner_id,
            created_at=now,
            updated_at=now,
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return map_project(new_project)

    @strawberry.mutation
    def updateProject(
        self,
        info,
        project_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        source: Optional[Source] = None,
        repository_id: Optional[int] = None,
        owner_id: Optional[int] = None,
    ) -> Project:
        """
        Updates an existing project.
        """
        db: Session = info.context["db"]
        project = db.query(Projects).filter(Projects.id == project_id).first()
        if not project:
            raise Exception(f"Project with id {project_id} not found")
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if url is not None:
            project.url = url
        if source is not None:
            project.source = source.value
        if repository_id is not None:
            project.repository_id = repository_id
        if owner_id is not None:
          


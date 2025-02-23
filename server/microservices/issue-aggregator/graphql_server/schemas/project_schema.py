"""
Define the open-source projects(e.g Linux Kernel, Kubernetes, Apache)
that are being tracked by the application that users can create or join.
Each project is stored as a dictionary with the following keys:
- project_id: The unique identifier of the project
- name: The name of the project
- description: The description of the project
- url: Direct link to the project's repository
- source: The source of the project (github/gitlab)
- repository_id: References the associated repository
- owner_id: References the user who created the project
- created_at: The date and time the project was created
- updated_at: The date and time the project was last updated
"""

import datetime
import strawberry
import enum
from typing import List, Union

@strawberry.enum
class Source(enum.Enum):
    GITHUB = "github"
    GITLAB = "gitlab"

@strawberry.type
class Project:
    project_id: int
    name: str
    description: str
    url: str
    source: Source
    repository_id: int
    owner_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

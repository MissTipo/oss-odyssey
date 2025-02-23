"""
Captures the information about the repository where the issue resides.
Each repository is stored as a dictionary with the following keys:
- id: Internal unique identifier.
- external_id: Repository ID from the source (e.g GitHub, GitLab).
- name: The name of the repository.
- full_name: The full name of the repository.
- description: The description of the repository.
- url: Direct link to the repository.
- source: The source of the repository (github/gitlab).
- language: The primary programming language used in the repository.
"""

import strawberry
import enum
from typing import List

@strawberry.enum
class Source(enum.Enum):
    GITHUB = "github"
    GITLAB = "gitlab"

@strawberry.type
class Repository:
    id: int
    external_id: strawberry.scalar(str)
    name: str
    full_name: str
    description: str
    url: str
    source: Source

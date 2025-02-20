"""
Stores the details of each aggregated issue from the GitHub or GitLab API.
Each issue is stored as a dictionary with the following keys:
- issue_id: The unique identifier of the issue
- title: The title of the issue
- description: The description of the issue
- state: The state of the issue (open or closed)
- created_at: The date and time the issue was created
- updated_at: The date and time the issue was last updated
- url: Direct link to the issue on GitHub/GitLab
- source: The source of the issue (github/gitlab)
- labels: List of labels associated with the issue
- repository_id: References the associated repository
"""

import datetime
from typing import List, Union
import enum
import strawberry

@strawberry.enum
class State(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"

@strawberry.enum
class Source(enum.Enum):
    GITHUB = "github"
    GITLAB = "gitlab"

@strawberry.type
class Issue:
    id: int
    external_id: strawberry.scalar(Union[str, int])
    title: str
    description: str
    state: State
    created_at: datetime.datetime
    updated_at: datetime.datetime
    url: str
    source: Source
    labels: List[str]
    repository_id: int

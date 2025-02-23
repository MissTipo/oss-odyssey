"""
Manage user-specific issues within a project, tracking progress and status.
Each issue is stored as a dictionary with the following keys:
- issue_id: The unique identifier of the issue
- issue: A reference to the aggregated issue (from issue schema) that the user is working on.
- project_id: References the associated project
- status: the current status of the issue in the user's workflow. Options include:
    - backlog: Issue has been identified but not yet started
    - in_progress: Issue is currently being worked on
    - completed: Issue has been completed
    - archived: Issue is no longer being worked on
    - dropped: If they decide to stop working on the issue
- pr_link: Direct link to the submitted pull request or patch
- created_at: The date and time the issue was created
- updated_at: The date and time the issue was last updated
"""

import datetime
import strawberry
import enum
from typing import List, Union

@strawberry.enum
class Status(enum.Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    DROPPED = "dropped"

@strawberry.type
class UserIssue:
    issue_id: int
    issue: int
    project_id: int
    status: Status
    pr_link: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

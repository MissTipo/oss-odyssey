# graphql_server/schemas/bookmark_schema.py
import strawberry
from datetime import datetime
from typing import Optional
from enum import Enum

class ProgressStatusEnum(str, Enum):
    to_do = "to_do"
    in_progress = "in_progress"
    completed = "completed"
    dropped = "dropped"

@strawberry.type
class Bookmark:
    id: int
    user_id: int
    issue_id: int
    status: ProgressStatusEnum
    pr_link: Optional[str]
    created_at: datetime
    updated_at: datetime

@strawberry.input
class CreateBookmarkInput:
    user_id: int
    issue_id: int
    status: ProgressStatusEnum
    pr_link: Optional[str] = None

@strawberry.input
class UpdateBookmarkInput:
    id: int
    status: Optional[ProgressStatusEnum] = None
    pr_link: Optional[str] = None


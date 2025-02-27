import strawberry
from datetime import datetime
from typing import Optional

@strawberry.type
class User:
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

@strawberry.input
class UpdateUserInput:
    id: int
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None



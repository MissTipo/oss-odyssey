import strawberry
from datetime import datetime

@strawberry.type
class User:
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


import strawberry
import enum
from typing import List
from .issue_schema import Source

@strawberry.type
class Repository:
    id: int
    external_id: strawberry.scalar(str)
    name: str
    full_name: str
    description: str
    url: str
    source: Source
    language: str
    

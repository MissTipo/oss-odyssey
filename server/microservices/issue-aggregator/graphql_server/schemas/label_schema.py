"""
Represents the labels/tags associated with each issue.
Each label is stored as a dictionary with the following keys:
- label_id: The unique identifier of the label
- name: The name of the label
- color: The color associated with the label
- description: The description of the label
- repository_id: References the associated repository.
"""
import strawberry
from typing import List

@strawberry.type
class Label:
    label_id: int
    name: str
    color: str
    description: str
    repository_id: int

"""
Implements the many-to-many relationship between issues and labels.
Each issue can have multiple labels and each label can be associated with multiple issues.
The IssueLabel schema captures this relationship with the following fields:
- id: Integer, Primary Key - Unique identifier for the issue-label association
- issue_id: Foreign Key - References the issue schema.
- label_id: Foreign Key - References the label schema.
"""

import strawberry
from typing import List

@strawberry.type
class IssueLabelAssociation:
    id: int
    issue_id: int
    label_id: int


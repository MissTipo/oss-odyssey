"""
Resolver for retrieving issue data from the database.
The QueryResolver handles the READ operations/retrieving data from the database.
The MutationResolver handles the write operations or CREATE, UPDATE, DELETE operations.
"""

import datetime
from typing import List, Optional, Union
from strawberry import ID
from graphql_server.schemas.issue_schema import Issue, State, Source

class QueryResolver:

    @staticmethod

    def get_issues() -> List[Issue]:
        """Retrieves a list of all aggregated issues """
        # TODO: Connect to data layer
        pass

    @staticmethod

    def get_issue_by_id(issue_id: ID) -> Optional[Issue]:
        """Retrieves a single issue by its ID"""
        return Issue.objects.get(id=issue_id)
    
    

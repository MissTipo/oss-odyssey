# graphql_server/resolvers/bookmark_resolver.py
import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
import strawberry
from models.models import UserIssue, ProgressStatus
from graphql_server.schemas.bookmark_schema import (
    Bookmark, 
    CreateBookmarkInput, 
    UpdateBookmarkInput, 
    ProgressStatusEnum
)

@strawberry.type
class BookmarkQueryResolver:
    @strawberry.field
    def get_bookmarks(self, info) -> list[Bookmark]:
        db: Session = info.context["db"]
        user_id = info.context.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user_issues = db.query(UserIssue).filter(UserIssue.user_id == user_id).all()
        return [
            Bookmark(
                id=issue.id,
                user_id=issue.user_id,
                issue_id=issue.issue_id,
                status=issue.status.value,
                pr_link=issue.pr_link,
                created_at=issue.created_at,
                updated_at=issue.updated_at
            )
            for issue in user_issues
        ]

@strawberry.type
class BookmarkMutationResolver:
    @strawberry.mutation
    def create_bookmark(self, info, input: CreateBookmarkInput) -> Bookmark:
        db: Session = info.context["db"]
        # Prevent duplicate bookmarks
        existing = db.query(UserIssue).filter(
            UserIssue.user_id == input.user_id,
            UserIssue.issue_id == input.issue_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bookmark already exists")
        new_bookmark = UserIssue(
            user_id=input.user_id,
            issue_id=input.issue_id,
            status=ProgressStatus(input.status),
            pr_link=input.pr_link,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        db.add(new_bookmark)
        db.commit()
        db.refresh(new_bookmark)
        return Bookmark(
            id=new_bookmark.id,
            user_id=new_bookmark.user_id,
            issue_id=new_bookmark.issue_id,
            status=new_bookmark.status.value,
            pr_link=new_bookmark.pr_link,
            created_at=new_bookmark.created_at,
            updated_at=new_bookmark.updated_at
        )

    @strawberry.mutation
    def update_bookmark(self, info, input: UpdateBookmarkInput) -> Bookmark:
        db: Session = info.context["db"]
        bookmark = db.query(UserIssue).filter(UserIssue.id == input.id).first()
        if not bookmark:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        if input.status is not None:
            bookmark.status = ProgressStatus(input.status)
        if input.pr_link is not None:
            bookmark.pr_link = input.pr_link
        bookmark.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(bookmark)
        return Bookmark(
            id=bookmark.id,
            user_id=bookmark.user_id,
            issue_id=bookmark.issue_id,
            status=bookmark.status.value,
            pr_link=bookmark.pr_link,
            created_at=bookmark.created_at,
            updated_at=bookmark.updated_at
        )

    @strawberry.mutation
    def delete_bookmark(self, info, id: int) -> Bookmark:
        db: Session = info.context["db"]
        bookmark = db.query(UserIssue).filter(UserIssue.id == id).first()
        if not bookmark:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        # Capture details before deletion
        deleted_bookmark = Bookmark(
            id=bookmark.id,
            user_id=bookmark.user_id,
            issue_id=bookmark.issue_id,
            status=bookmark.status.value,
            pr_link=bookmark.pr_link,
            created_at=bookmark.created_at,
            updated_at=bookmark.updated_at
        )
        db.delete(bookmark)
        db.commit()
        return deleted_bookmark


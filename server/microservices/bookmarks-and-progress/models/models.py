# models/models.py
import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from models.database import Base

class ProgressStatus(enum.Enum):
    to_do = "to_do"
    in_progress = "in_progress"
    completed = "completed"
    dropped = "dropped"

class UserIssue(Base):
    __tablename__ = "user_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # In production, this might be a foreign key to a User service
    issue_id = Column(Integer, index=True)  # Same for Issue; it could be a foreign key to an Issues service
    status = Column(Enum(ProgressStatus), default=ProgressStatus.to_do, nullable=False)
    pr_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
         Index('ix_user_issue', "user_id", "issue_id", unique=True),
    )

    def __repr__(self):
        return f"<UserIssue(id={self.id}, user_id={self.user_id}, issue_id={self.issue_id}, status='{self.status.value}')>"


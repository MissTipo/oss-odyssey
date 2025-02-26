import os
import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from .database import Base

# Use JSONB by default, but if running tests with SQLite, use JSON.
if os.getenv("TESTING", "0") == "1":
    json_type = JSON
else:
    json_type = JSONB

class Issues(Base):
    """ Issues Model """

    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, nullable=True)
    title = Column(Text, nullable=False)
    description = Column(String(200), nullable=True)
    state = Column(Boolean, default= False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=True)
    url = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    labels = Column(MutableList.as_mutable(json_type), nullable=True)
    repository_id = Column(Integer, nullable=True)


    def __repr__(self):
        return '<Issue %r>' % (self.title)

class Labels(Base):
    __tablename__ = 'labels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    repository_id = Column(Integer, nullable=False)  # Optionally: ForeignKey('repositories.id')

    def __repr__(self):
        return f"<Label(id={self.id}, name='{self.name}')>"

class Repositories(Base):
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)  # Expected values: 'github' or 'gitlab'
    language = Column(String, nullable=True)

    def __repr__(self):
        return f"<Repository(id={self.id}, name='{self.name}')>"


class Projects(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)  # Expected values: 'github' or 'gitlab'
    repository_id = Column(Integer, nullable=False)  # Optionally: ForeignKey('repositories.id')
    owner_id = Column(Integer, nullable=False)  # Optionally: ForeignKey('users.id')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

class UserIssues(Base):
    __tablename__ = 'user_issues'
    
    id = Column(Integer, primary_key=True)
    issue = Column(Integer, nullable=False)  # Reference to the aggregated issue (could be a ForeignKey)
    project_id = Column(Integer, nullable=False)  # Optionally: ForeignKey('projects.id')
    status = Column(String, nullable=False)  # Expected values: 'backlog', 'in_progress', 'completed', 'archived', 'dropped'
    pr_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<UserIssue(id={self.id}, issue={self.issue}, status='{self.status}')>"


class IssueLabel(Base):
    __tablename__ = 'issue_label'
    
    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, nullable=False)  # Optionally: ForeignKey('issues.id')
    label_id = Column(Integer, nullable=False)  # Optionally: ForeignKey('labels.id')

    def __repr__(self):
        return f"<IssueLabel(id={self.id}, issue_id={self.issue_id}, label_id={self.label_id})>"


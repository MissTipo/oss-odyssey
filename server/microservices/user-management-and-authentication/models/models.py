import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship for OAuth credentials, if needed
    oauth_credentials = relationship("OAuthCredential", back_populates="user", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class OAuthCredential(Base):
    __tablename__ = "oauth_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)  # e.g., "github"
    provider_user_id = Column(String, nullable=False, unique=True)
    access_token = Column(String, nullable=True)  # Optionally store the OAuth token
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    user = relationship("User", back_populates="oauth_credentials")
    def __repr__(self):
        return f"<OAuthCredential(id={self.id}, provider='{self.provider}', user_id={self.user_id})>"


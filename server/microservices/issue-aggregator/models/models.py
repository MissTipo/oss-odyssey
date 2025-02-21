from sqlalchemy import Column, Integer, String, Boolean, Text
from .database import Base

class Issues(Base):
    """ Issues Model """

    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, nullable=True)
    title = Column(Text, nullable=False)
    description = Column(String(200), nullable=True)
    state = Column(Boolean, default= False)
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)
    url = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    labels = Column(Text, nullable=True)
    repository_id = Column(Integer, nullable=True)

    """def __init__(self, title=None, description=None, status=None):
        self.title = title
        self.description = description
        self.state = state
        self.source = source"""

    def __repr__(self):
        return '<Issue %r>' % (self.title)

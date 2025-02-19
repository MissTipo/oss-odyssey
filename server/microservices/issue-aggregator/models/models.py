from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Issues(Base):
    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(200))
    state = Column(Boolean)
    
    source = Column(String(50))

    def __init__(self, title=None, description=None, status=None):
        self.title = title
        self.description = description
        self.status = status

    def __repr__(self):
        return '<Issue %r>' % (self.title)

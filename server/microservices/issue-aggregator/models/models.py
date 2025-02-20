from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Issues(Base):
    """ Issues Model """

    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    state = Column(Boolean, default= False)
    source = Column(String(50), nullable=True)

    """def __init__(self, title=None, description=None, status=None):
        self.title = title
        self.description = description
        self.state = state
        self.source = source"""

    def __repr__(self):
        return '<Issue %r>' % (self.title)

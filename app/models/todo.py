from sqlalchemy import Column,Integer,String,Boolean,DateTime,Text,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Todo(Base):
    __tablename__='todos'

    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,nullable=False)
    description=Column(Text,nullable=False)
    is_completed=Column(Boolean,default=False)
    priority=Column(String,default='medium')
    category=Column(String,nullable=True)
    due_date=Column(DateTime(timezone=True),nullable=True)

    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())
    completed_at=Column(DateTime(timezone=True),nullable=True)
    
    owner_id=Column(Integer,ForeignKey('users.id'),nullable=False)
    owner=relationship('User',back_populates='todos')
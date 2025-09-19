from sqlalchemy import Column,Integer,String,Boolean,DateTime,Text
from sqlalchemy.sql import func 
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__='users'

    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,index=True)
    username=Column(String,unique=True,index=True)
    full_name=Column(String,nullable=True)
    hashed_password=Column(String,nullable=True)
    is_active=Column(Boolean,default=True)
    is_verified=Column(Boolean,default=False)
    is_admin=Column(Boolean,default=False)
    google_id=Column(String,nullable=True)
    profile_picture=Column(String,nullable=True)

    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())

    todos=relationship('Todo',back_populates='owner',cascade='all,delete-orphan')
    habits=relationship('Habit',back_populates='owner',cascade='all,delete-orphan')
    pomodoro_sessions=relationship('PomodoroSession',back_populates='owner',cascade='all,delete-orphan')
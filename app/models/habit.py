from sqlalchemy import Column,Integer,String,Boolean,DateTime,Text,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Habit(Base):
    __tablename__='habits'


    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    description=Column(Text,nullable=False)
    frequency=Column(String,default='daily')
    target_count=Column(Integer,default=1)
    is_active=Column(Boolean,default=True)
    streak_count=Column(Integer,default=0)
    best_streak=Column(Integer,default=0)


    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())
    
    
    owner_id=Column(Integer,ForeignKey('users.id'),nullable=False)
    owner=relationship('User',back_populates='habits')

    entries=relationship('HabitEntry',back_populates='habit',cascade='all,delete-orphan')



class HabitEntry(Base):
    __tablename__='habit_entries'

    id=Column(Integer,primary_key=True,index=True)
    completed_count=Column(Integer,default=1)
    notes=Column(Text,nullable=True)
    date=Column(DateTime(timezone=True),nullable=False,server_default=func.current_date())
    habit_id=Column(Integer,ForeignKey('habits.id'),nullable=False)
    habit=relationship('Habit',back_populates='entries')


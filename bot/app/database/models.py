from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from datetime import datetime
from app.database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, index=True)
    lat = Column(Float)
    lon = Column(Float)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    author = Column(ForeignKey('users.tg_id'))
    text = Column(String(100))
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

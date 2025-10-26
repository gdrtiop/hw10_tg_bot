from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, primary_key=True)
    location = Column(String(100))


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    author = Column(ForeignKey('users.id'))
    text = Column(String(250))
    done = Column(Boolean)
    created_at = Column()
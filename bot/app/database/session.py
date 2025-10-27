from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.database import url

DATABASE_URL = url

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
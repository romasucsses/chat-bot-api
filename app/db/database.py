import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(
    os.getenv('DATABASE_URL'), pool_size=10, max_overflow=20, echo=True
)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
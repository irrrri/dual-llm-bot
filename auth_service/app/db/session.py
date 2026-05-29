from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

DATABASE_URL = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"

engine = create_async_engine(DATABASE_URL, echo=settings.ENV == "local")
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    """Возвращает асинхронную сессию БД для использования"""
    async with AsyncSessionLocal() as session:
        yield session
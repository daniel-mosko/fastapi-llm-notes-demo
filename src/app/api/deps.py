from collections.abc import AsyncGenerator

from app.core.database import session_manager
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in session_manager.get_session():
        yield session

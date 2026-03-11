import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.config.logger import get_logger

logger = get_logger(__name__)


# NOTE: source [https://dev.to/akarshan/asynchronous-database-sessions-in-fastapi-with-sqlalchemy-1o7e]
class SessionManager:
    """Manages asynchronous DB sessions with connection pooling."""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def init_db(self, database_url: str | None = None, is_test=False) -> None:
        """Initialize the database engine and session factory."""
        logger.info("Initializing DB")
        if not database_url:
            if is_test:
                database_url = os.getenv("DATABASE_TEST_URL")
            else:
                database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise RuntimeError("DATABASE_URL environment variable not set")

        # Ensure async database URL
        if not database_url.startswith(
            (
                "postgresql+asyncpg://",
                "sqlite+aiosqlite://",
                "mysql+aiomysql://",
            )
        ):
            logger.warning(
                f"Database URL might not be async compatible: {database_url}"
            )

        self.engine = create_async_engine(
            database_url,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=5,  # default pool size
            max_overflow=10,  # default max overflow
            pool_pre_ping=True,
            pool_recycle=3600,  # default recycle time in seconds
            echo=False,  # set to True for SQL debug logging
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            close_resets_only=False,
        )

    async def close(self) -> None:
        """Dispose of the database engine."""
        if self.engine:
            logger.info("Closing database engine...")
            await self.engine.dispose()
            logger.info("Database engine closed.")

    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        """Yield a database session."""
        if not self.session_factory:
            raise RuntimeError("Database session factory is not initialized.")

        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


session_manager = SessionManager()

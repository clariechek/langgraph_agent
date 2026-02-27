"""
Database connection management.

Provides utilities for creating database connections, sessions,
and managing the connection lifecycle.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import get_settings
from src.db.models import Base


def get_engine(echo: bool = False):
    """
    Create a SQLAlchemy engine.
    
    Args:
        echo: If True, log all SQL statements (useful for debugging)
    
    Returns:
        SQLAlchemy Engine instance
    """
    settings = get_settings()
    return create_engine(
        settings.database_url_sync,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        echo=echo,
    )


def get_session_factory(engine=None) -> sessionmaker:
    """
    Create a session factory.
    
    Args:
        engine: Optional engine instance. If not provided, creates one.
    
    Returns:
        SQLAlchemy sessionmaker instance
    """
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Provides a transactional scope around a series of operations.
    Automatically commits on success and rolls back on error.
    
    Usage:
        with get_session() as session:
            entity = Entity(name="test", ...)
            session.add(entity)
            # Commits automatically when exiting the context
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine=None) -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called once at application startup or during
    development to create the database schema.
    
    Args:
        engine: Optional engine instance. If not provided, creates one.
    """
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_db(engine=None) -> None:
    """
    Drop all database tables.
    
    WARNING: This is destructive and should only be used in testing
    or development environments.
    
    Args:
        engine: Optional engine instance. If not provided, creates one.
    """
    if engine is None:
        engine = get_engine()
    Base.metadata.drop_all(bind=engine)

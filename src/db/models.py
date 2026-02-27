"""
SQLAlchemy ORM models for database tables.

These models define the database schema. We start with minimal models
for the ReAct agent and add more as we build additional agents.

Current models (ReAct agent):
- AgentRun: Tracks agent executions for observability
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class AgentRun(Base, TimestampMixin):
    """
    Agent execution runs for observability.
    
    Tracks each agent invocation with its inputs, outputs, and metrics.
    This is used for debugging, monitoring, and evaluation.
    """

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True, index=True
    )
    agent_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # "react" for now, later "rag", "chatbot", etc.
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="running"
    )  # "running", "success", "error"
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_count_input: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_count_output: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata", JSONB, nullable=True, default=dict
    )

    def __repr__(self) -> str:
        return f"<AgentRun(id={self.id}, run_id='{self.run_id}', status='{self.status}')>"

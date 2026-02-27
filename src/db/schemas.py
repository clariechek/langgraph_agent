"""
Pydantic schemas for database records.

These schemas are used for:
- Data validation before inserting into database
- Serialization/deserialization of database records
- API request/response models

We start with minimal schemas for the ReAct agent and add more
as we build additional agents.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentRunBase(BaseModel):
    """Base schema for AgentRun - shared fields for create and read."""

    run_id: str = Field(..., min_length=1, max_length=36)
    agent_type: str = Field(default="react", max_length=50)  # "react" for now
    input_text: str = Field(..., min_length=1)
    output_text: Optional[str] = Field(default=None)
    status: Literal["running", "success", "error"] = Field(default="running")
    error_message: Optional[str] = Field(default=None)
    latency_ms: Optional[int] = Field(default=None, ge=0)
    token_count_input: Optional[int] = Field(default=None, ge=0)
    token_count_output: Optional[int] = Field(default=None, ge=0)
    metadata_: Optional[dict] = Field(default=None, alias="metadata")

    model_config = ConfigDict(populate_by_name=True)


class AgentRunCreate(AgentRunBase):
    """Schema for creating a new AgentRun."""

    pass


class AgentRunRecord(AgentRunBase):
    """Schema for AgentRun records from database (includes id and timestamps)."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

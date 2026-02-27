"""Unit tests for database schemas and alignment validation."""

import pytest
from datetime import datetime

from src.db.schemas import AgentRunBase, AgentRunCreate, AgentRunRecord
from src.schemas.validators import validate_schema_alignment


class TestAgentRunSchemas:
    """Tests for AgentRun Pydantic schemas."""

    def test_agent_run_create_minimal(self):
        """AgentRunCreate should work with minimal required fields."""
        run = AgentRunCreate(
            run_id="test-123",
            input_text="What is 2+2?"
        )
        assert run.run_id == "test-123"
        assert run.input_text == "What is 2+2?"
        assert run.status == "running"  # default
        assert run.agent_type == "react"  # default

    def test_agent_run_create_full(self):
        """AgentRunCreate should accept all fields."""
        run = AgentRunCreate(
            run_id="test-456",
            agent_type="react",
            input_text="Calculate 10 * 5",
            output_text="The answer is 50",
            status="success",
            latency_ms=150,
            token_count_input=10,
            token_count_output=5,
            metadata={"tool_calls": 1}
        )
        assert run.output_text == "The answer is 50"
        assert run.latency_ms == 150
        assert run.metadata_ == {"tool_calls": 1}

    def test_agent_run_status_validation(self):
        """Status must be one of the allowed values."""
        # Valid statuses
        for status in ["running", "success", "error"]:
            run = AgentRunCreate(
                run_id="test",
                input_text="test",
                status=status
            )
            assert run.status == status
        
        # Invalid status
        with pytest.raises(ValueError):
            AgentRunCreate(
                run_id="test",
                input_text="test",
                status="invalid"
            )

    def test_agent_run_latency_must_be_positive(self):
        """Latency must be >= 0."""
        with pytest.raises(ValueError):
            AgentRunCreate(
                run_id="test",
                input_text="test",
                latency_ms=-1
            )

    def test_agent_run_record_from_attributes(self):
        """AgentRunRecord should work with from_attributes for ORM."""
        # Simulate an ORM object
        class MockORM:
            id = 1
            run_id = "test-123"
            agent_type = "react"
            input_text = "test input"
            output_text = "test output"
            status = "success"
            error_message = None
            latency_ms = 100
            token_count_input = 10
            token_count_output = 5
            metadata_ = {"key": "value"}
            created_at = datetime.now()
            updated_at = datetime.now()
        
        record = AgentRunRecord.model_validate(MockORM())
        assert record.id == 1
        assert record.run_id == "test-123"


class TestSchemaAlignment:
    """Tests for schema alignment validation."""

    def test_agent_run_schemas_aligned(self):
        """AgentRunCreate fields should be subset of AgentRunRecord."""
        errors = validate_schema_alignment(
            llm_schema=AgentRunCreate,
            db_schema=AgentRunRecord,
            strict=False
        )
        assert len(errors) == 0, f"Schema misalignment: {errors}"

    def test_alignment_detects_missing_fields(self):
        """Validation should detect fields missing in DB schema."""
        from pydantic import BaseModel
        
        class LLMOutput(BaseModel):
            name: str
            extra_field: str  # Not in DB
        
        class DBRecord(BaseModel):
            name: str
            id: int
        
        errors = validate_schema_alignment(LLMOutput, DBRecord)
        assert len(errors) == 1
        assert "extra_field" in errors[0]

    def test_alignment_detects_type_mismatch(self):
        """Validation should detect type mismatches."""
        from pydantic import BaseModel
        
        class LLMOutput(BaseModel):
            count: str  # String in LLM
        
        class DBRecord(BaseModel):
            count: int  # Int in DB
        
        errors = validate_schema_alignment(LLMOutput, DBRecord)
        assert len(errors) == 1
        assert "Type mismatch" in errors[0]

    def test_alignment_allows_numeric_compatibility(self):
        """int and float should be considered compatible."""
        from pydantic import BaseModel
        
        class LLMOutput(BaseModel):
            score: int
        
        class DBRecord(BaseModel):
            score: float
        
        errors = validate_schema_alignment(LLMOutput, DBRecord)
        assert len(errors) == 0  # Should be compatible

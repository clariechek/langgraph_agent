"""
Schema alignment validation utilities.

These utilities help ensure that:
1. LLM response schemas can be stored in database tables
2. Pydantic schemas match their SQLAlchemy counterparts
3. Schema changes are caught by tests before deployment

Usage:
    from src.schemas.validators import validate_schema_alignment
    
    errors = validate_schema_alignment(
        llm_schema=ExtractedEntity,
        db_schema=EntityRecord
    )
    assert len(errors) == 0, f"Schema drift detected: {errors}"
"""

from typing import Any, Type, get_args, get_origin

from pydantic import BaseModel


def validate_schema_alignment(
    llm_schema: Type[BaseModel],
    db_schema: Type[BaseModel],
    strict: bool = False,
) -> list[str]:
    """
    Validate that LLM response schema fields can be stored in DB schema.
    
    This ensures that when an LLM returns structured output, all fields
    can be mapped to the database record schema.
    
    Args:
        llm_schema: Pydantic model for LLM structured output
        db_schema: Pydantic model for database records
        strict: If True, require exact field match. If False (default),
                only require LLM fields to be a subset of DB fields.
    
    Returns:
        List of error messages. Empty list means schemas are aligned.
    
    Example:
        errors = validate_schema_alignment(
            llm_schema=ExtractedEntity,  # LLM output
            db_schema=EntityRecord,      # DB record
        )
    """
    errors = []
    
    llm_fields = set(llm_schema.model_fields.keys())
    db_fields = set(db_schema.model_fields.keys())
    
    # Check if LLM fields are subset of DB fields
    missing_in_db = llm_fields - db_fields
    if missing_in_db:
        errors.append(
            f"Fields in {llm_schema.__name__} missing from {db_schema.__name__}: "
            f"{missing_in_db}"
        )
    
    # In strict mode, also check for extra DB fields (excluding id, timestamps)
    if strict:
        db_only_fields = db_fields - llm_fields - {"id", "created_at", "updated_at"}
        if db_only_fields:
            errors.append(
                f"Fields in {db_schema.__name__} not in {llm_schema.__name__}: "
                f"{db_only_fields}"
            )
    
    # Check type compatibility for shared fields
    for field_name in llm_fields & db_fields:
        llm_field = llm_schema.model_fields[field_name]
        db_field = db_schema.model_fields[field_name]
        
        llm_type = _normalize_type(llm_field.annotation)
        db_type = _normalize_type(db_field.annotation)
        
        if not _types_compatible(llm_type, db_type):
            errors.append(
                f"Type mismatch for field '{field_name}': "
                f"{llm_schema.__name__}.{field_name} is {llm_field.annotation}, "
                f"{db_schema.__name__}.{field_name} is {db_field.annotation}"
            )
    
    return errors


def _normalize_type(type_hint: Any) -> Any:
    """Normalize a type hint for comparison."""
    origin = get_origin(type_hint)
    
    # Handle Optional types - extract the inner type
    if origin is type(None):
        return type(None)
    
    # For Union types (including Optional), get the non-None type
    if origin:
        args = get_args(type_hint)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return non_none_args[0]
    
    return type_hint


def _types_compatible(type1: Any, type2: Any) -> bool:
    """
    Check if two types are compatible.
    
    Types are compatible if:
    - They are the same type
    - One is Optional version of the other
    - Both are numeric types (int, float)
    """
    # Exact match
    if type1 == type2:
        return True
    
    # Handle Optional - unwrap and compare
    type1_inner = _unwrap_optional(type1)
    type2_inner = _unwrap_optional(type2)
    
    if type1_inner == type2_inner:
        return True
    
    # Numeric compatibility
    numeric_types = {int, float}
    if type1_inner in numeric_types and type2_inner in numeric_types:
        return True
    
    return False


def _unwrap_optional(type_hint: Any) -> Any:
    """Unwrap Optional[T] to get T."""
    origin = get_origin(type_hint)
    if origin:
        args = get_args(type_hint)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return non_none_args[0]
    return type_hint


def validate_table_has_schema(
    table_names: list[str],
    schema_registry: dict[str, Type[BaseModel]],
) -> list[str]:
    """
    Validate that every table name has a corresponding schema.
    
    This prevents the common error of adding a table name constant
    but forgetting to create its Pydantic schema.
    
    Args:
        table_names: List of table name strings
        schema_registry: Dict mapping table names to Pydantic schemas
    
    Returns:
        List of error messages for tables without schemas
    """
    errors = []
    
    for table_name in table_names:
        if table_name not in schema_registry:
            errors.append(f"Table '{table_name}' has no registered schema")
    
    return errors

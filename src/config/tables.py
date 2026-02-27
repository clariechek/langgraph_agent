"""
Table name management for bronze/silver/gold data layers.

This module provides type-safe table name generation that:
- Prevents typos through Enums
- Handles environment prefixing (local/dev/stg/prod)
- Handles data layer prefixing (bronze/silver/gold)
- Provides a centralized registry for all table names

Usage:
    from src.config.tables import TableNameManager, DataLayer, TableName
    
    manager = TableNameManager(env="dev", layer=DataLayer.SILVER)
    table = manager.get(TableName.AGENT_RUNS)  # "dev_silver_agent_runs"
"""

from enum import Enum
from typing import Literal

from src.config.settings import get_settings


class DataLayer(str, Enum):
    """
    Data layer in the medallion architecture.
    
    - BRONZE: Raw data, minimal processing
    - SILVER: Cleaned, validated, deduplicated
    - GOLD: Aggregated, business-ready
    """

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class TableName(str, Enum):
    """
    Registry of all table names in the application.
    
    Using an Enum ensures:
    - No typos in table names (IDE catches errors)
    - Easy refactoring (rename in one place)
    - Discoverability (autocomplete shows all tables)
    
    Add new tables here as the application grows.
    """

    # Core tables (ReAct agent)
    AGENT_RUNS = "agent_runs"

    # Future tables (uncomment as agents are built)
    # ENTITIES = "entities"           # Entity extraction
    # CONVERSATIONS = "conversations" # Chatbot
    # MESSAGES = "messages"           # Chatbot messages
    # DOCUMENTS = "documents"         # RAG documents
    # EMBEDDINGS = "embeddings"       # RAG vector store


EnvironmentType = Literal["local", "dev", "stg", "prod"]


class TableNameManager:
    """
    Generates fully-qualified table names with environment and layer prefixes.
    
    Table naming convention: {environment}_{layer}_{table_name}
    
    Examples:
        - local_bronze_agent_runs
        - dev_silver_agent_runs
        - prod_gold_agent_runs
    
    This allows:
        - Multiple environments in the same database (useful for dev/test)
        - Clear separation of data layers
        - Easy identification of table purpose
    """

    def __init__(
        self,
        env: EnvironmentType | None = None,
        layer: DataLayer = DataLayer.SILVER,
    ):
        """
        Initialize the table name manager.
        
        Args:
            env: Environment name. If None, reads from settings.
            layer: Data layer (bronze/silver/gold). Defaults to silver.
        """
        if env is None:
            settings = get_settings()
            env = settings.app_environment
        
        self.env = env
        self.layer = layer

    def get(self, table: TableName) -> str:
        """
        Get the fully-qualified table name.
        
        Args:
            table: Table name from the TableName enum
        
        Returns:
            Fully-qualified table name with environment and layer prefix
        
        Example:
            manager.get(TableName.AGENT_RUNS)  # "dev_silver_agent_runs"
        """
        return f"{self.env}_{self.layer.value}_{table.value}"

    def get_all(self) -> dict[TableName, str]:
        """
        Get all table names with their fully-qualified versions.
        
        Returns:
            Dict mapping TableName enum to fully-qualified name
        """
        return {table: self.get(table) for table in TableName}

    def __repr__(self) -> str:
        return f"TableNameManager(env='{self.env}', layer='{self.layer.value}')"


def get_table_manager(
    layer: DataLayer = DataLayer.SILVER,
) -> TableNameManager:
    """
    Factory function to create a TableNameManager with current environment.
    
    Args:
        layer: Data layer to use (defaults to SILVER)
    
    Returns:
        TableNameManager configured for current environment
    """
    return TableNameManager(env=None, layer=layer)

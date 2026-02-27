"""Unit tests for table name management."""

import pytest

from src.config.tables import (
    DataLayer,
    TableName,
    TableNameManager,
    get_table_manager,
)


class TestDataLayer:
    """Tests for DataLayer enum."""

    def test_data_layer_values(self):
        """DataLayer enum should have correct values."""
        assert DataLayer.BRONZE.value == "bronze"
        assert DataLayer.SILVER.value == "silver"
        assert DataLayer.GOLD.value == "gold"

    def test_data_layer_is_string_enum(self):
        """DataLayer should be usable as string via .value."""
        assert DataLayer.BRONZE.value == "bronze"
        assert f"prefix_{DataLayer.SILVER.value}" == "prefix_silver"


class TestTableName:
    """Tests for TableName enum."""

    def test_agent_runs_table_exists(self):
        """AGENT_RUNS table should be defined."""
        assert TableName.AGENT_RUNS.value == "agent_runs"

    def test_table_name_is_string_enum(self):
        """TableName should be usable as string via .value."""
        assert TableName.AGENT_RUNS.value == "agent_runs"


class TestTableNameManager:
    """Tests for TableNameManager class."""

    def test_get_table_with_explicit_env(self):
        """Should generate correct table name with explicit environment."""
        manager = TableNameManager(env="dev", layer=DataLayer.SILVER)
        
        result = manager.get(TableName.AGENT_RUNS)
        
        assert result == "dev_silver_agent_runs"

    def test_get_table_different_environments(self):
        """Should handle all environment types."""
        test_cases = [
            ("local", "local_silver_agent_runs"),
            ("dev", "dev_silver_agent_runs"),
            ("stg", "stg_silver_agent_runs"),
            ("prod", "prod_silver_agent_runs"),
        ]
        
        for env, expected in test_cases:
            manager = TableNameManager(env=env, layer=DataLayer.SILVER)
            assert manager.get(TableName.AGENT_RUNS) == expected

    def test_get_table_different_layers(self):
        """Should handle all data layers."""
        test_cases = [
            (DataLayer.BRONZE, "dev_bronze_agent_runs"),
            (DataLayer.SILVER, "dev_silver_agent_runs"),
            (DataLayer.GOLD, "dev_gold_agent_runs"),
        ]
        
        for layer, expected in test_cases:
            manager = TableNameManager(env="dev", layer=layer)
            assert manager.get(TableName.AGENT_RUNS) == expected

    def test_get_all_tables(self):
        """get_all should return all table names."""
        manager = TableNameManager(env="dev", layer=DataLayer.SILVER)
        
        all_tables = manager.get_all()
        
        assert isinstance(all_tables, dict)
        assert TableName.AGENT_RUNS in all_tables
        assert all_tables[TableName.AGENT_RUNS] == "dev_silver_agent_runs"

    def test_manager_repr(self):
        """Manager should have readable repr."""
        manager = TableNameManager(env="prod", layer=DataLayer.GOLD)
        
        result = repr(manager)
        
        assert "prod" in result
        assert "gold" in result

    def test_default_layer_is_silver(self):
        """Default layer should be SILVER."""
        manager = TableNameManager(env="dev")
        
        assert manager.layer == DataLayer.SILVER

    def test_env_from_settings_when_none(self, monkeypatch):
        """Should read environment from settings when not provided."""
        monkeypatch.setenv("APP_ENVIRONMENT", "stg")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        
        # Clear settings cache to pick up new env var
        from src.config.settings import get_settings
        get_settings.cache_clear()
        
        manager = TableNameManager(env=None, layer=DataLayer.SILVER)
        
        assert manager.env == "stg"


class TestGetTableManager:
    """Tests for get_table_manager factory function."""

    def test_creates_manager_with_default_layer(self, monkeypatch):
        """Factory should create manager with SILVER as default."""
        monkeypatch.setenv("APP_ENVIRONMENT", "dev")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        
        from src.config.settings import get_settings
        get_settings.cache_clear()
        
        manager = get_table_manager()
        
        assert manager.layer == DataLayer.SILVER

    def test_creates_manager_with_specified_layer(self, monkeypatch):
        """Factory should accept layer parameter."""
        monkeypatch.setenv("APP_ENVIRONMENT", "dev")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        
        from src.config.settings import get_settings
        get_settings.cache_clear()
        
        manager = get_table_manager(layer=DataLayer.GOLD)
        
        assert manager.layer == DataLayer.GOLD


class TestTableNameTypeSafety:
    """Tests demonstrating type safety benefits."""

    def test_typo_would_fail_at_import(self):
        """
        This test documents that typos are caught by the type system.
        
        If you try to use TableName.AGENT_RUN (missing 'S'), 
        the IDE will show an error and the code won't run.
        """
        # This would fail: TableName.AGENT_RUN  (AttributeError)
        # This works: TableName.AGENT_RUNS
        assert hasattr(TableName, "AGENT_RUNS")
        assert not hasattr(TableName, "AGENT_RUN")  # Typo doesn't exist

    def test_all_tables_are_strings(self):
        """All table names should be valid strings."""
        for table in TableName:
            assert isinstance(table.value, str)
            assert len(table.value) > 0
            assert "_" not in table.value or table.value.count("_") <= 2

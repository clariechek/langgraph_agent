"""Unit tests for prompt management."""

import pytest
from pathlib import Path

from src.prompts.registry import PromptTemplate, PromptRegistry


class TestPromptTemplate:
    """Tests for PromptTemplate class."""

    def test_create_minimal_prompt(self):
        """Should create prompt with minimal required fields."""
        prompt = PromptTemplate(
            name="test_prompt",
            template="Hello {name}!",
            variables=["name"]
        )
        
        assert prompt.name == "test_prompt"
        assert prompt.version == "1.0.0"  # default
        assert prompt.variables == ["name"]

    def test_format_with_variables(self):
        """Should format template with provided variables."""
        prompt = PromptTemplate(
            name="greeting",
            template="Hello {name}, welcome to {place}!",
            variables=["name", "place"]
        )
        
        result = prompt.format(name="Alice", place="Wonderland")
        
        assert result == "Hello Alice, welcome to Wonderland!"

    def test_format_missing_variable_raises_error(self):
        """Should raise KeyError when required variable is missing."""
        prompt = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name"]
        )
        
        with pytest.raises(KeyError) as exc_info:
            prompt.format()  # Missing 'name'
        
        assert "name" in str(exc_info.value)

    def test_format_extra_variables_allowed(self):
        """Extra variables should be silently ignored."""
        prompt = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name"]
        )
        
        result = prompt.format(name="Bob", extra="ignored")
        
        assert result == "Hello Bob!"

    def test_validate_variables_success(self):
        """Should return empty list when variables match placeholders."""
        prompt = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name"]
        )
        
        errors = prompt.validate_variables()
        
        assert errors == []

    def test_validate_variables_undeclared(self):
        """Should detect undeclared placeholders in template."""
        prompt = PromptTemplate(
            name="test",
            template="Hello {name} from {place}!",
            variables=["name"]  # Missing 'place'
        )
        
        errors = prompt.validate_variables()
        
        assert len(errors) == 1
        assert "place" in errors[0]

    def test_validate_variables_unused(self):
        """Should detect declared but unused variables."""
        prompt = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name", "unused_var"]
        )
        
        errors = prompt.validate_variables()
        
        assert len(errors) == 1
        assert "unused_var" in errors[0]

    def test_variables_coerced_to_list(self):
        """Single string variable should be converted to list."""
        prompt = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables="name"  # Single string
        )
        
        assert prompt.variables == ["name"]

    def test_none_variables_becomes_empty_list(self):
        """None variables should become empty list."""
        prompt = PromptTemplate(
            name="test",
            template="Hello world!",
            variables=None
        )
        
        assert prompt.variables == []


class TestPromptRegistry:
    """Tests for PromptRegistry class."""

    def test_register_and_get_prompt(self):
        """Should register and retrieve prompts."""
        registry = PromptRegistry()
        prompt = PromptTemplate(
            name="test_prompt",
            template="Test {var}",
            variables=["var"]
        )
        
        registry.register(prompt)
        retrieved = registry.get("test_prompt")
        
        assert retrieved.name == "test_prompt"

    def test_get_unknown_prompt_raises_error(self):
        """Should raise KeyError for unknown prompt."""
        registry = PromptRegistry()
        
        with pytest.raises(KeyError) as exc_info:
            registry.get("nonexistent")
        
        assert "nonexistent" in str(exc_info.value)

    def test_list_prompts(self):
        """Should list all registered prompt names."""
        registry = PromptRegistry()
        registry.register(PromptTemplate(name="prompt1", template="Test"))
        registry.register(PromptTemplate(name="prompt2", template="Test"))
        
        names = registry.list_prompts()
        
        assert "prompt1" in names
        assert "prompt2" in names

    def test_load_from_yaml(self, tmp_path):
        """Should load prompt from YAML file."""
        yaml_content = """
name: yaml_prompt
version: "2.0.0"
description: A test prompt
template: "Hello {name}!"
variables:
  - name
"""
        yaml_file = tmp_path / "test_prompt.yaml"
        yaml_file.write_text(yaml_content)
        
        registry = PromptRegistry()
        prompt = registry.load_from_yaml(yaml_file)
        
        assert prompt.name == "yaml_prompt"
        assert prompt.version == "2.0.0"
        assert registry.get("yaml_prompt") == prompt

    def test_load_from_directory(self, tmp_path):
        """Should load all YAML prompts from directory."""
        # Create test YAML files
        (tmp_path / "prompt1.yaml").write_text("""
name: prompt1
template: "Test 1"
""")
        (tmp_path / "prompt2.yaml").write_text("""
name: prompt2
template: "Test 2"
""")
        
        registry = PromptRegistry()
        prompts = registry.load_from_directory(tmp_path)
        
        assert len(prompts) == 2
        assert "prompt1" in registry.list_prompts()
        assert "prompt2" in registry.list_prompts()

    def test_validate_all_prompts(self):
        """Should validate all registered prompts."""
        registry = PromptRegistry()
        
        # Valid prompt
        registry.register(PromptTemplate(
            name="valid",
            template="Hello {name}!",
            variables=["name"]
        ))
        
        # Invalid prompt (undeclared variable)
        registry.register(PromptTemplate(
            name="invalid",
            template="Hello {name} {missing}!",
            variables=["name"]
        ))
        
        errors = registry.validate_all()
        
        assert "valid" not in errors
        assert "invalid" in errors
        assert "missing" in errors["invalid"][0]


class TestActualPromptFiles:
    """Tests for the actual prompt YAML files in the project."""

    def test_react_reasoning_prompt_exists(self):
        """react_reasoning.yaml should exist and be valid."""
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        prompt_file = prompts_dir / "react_reasoning.yaml"
        
        assert prompt_file.exists(), f"Missing {prompt_file}"
        
        registry = PromptRegistry()
        prompt = registry.load_from_yaml(prompt_file)
        
        assert prompt.name == "react_reasoning"
        assert "tools" in prompt.variables
        assert "question" in prompt.variables

    def test_react_tool_response_prompt_exists(self):
        """react_tool_response.yaml should exist and be valid."""
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        prompt_file = prompts_dir / "react_tool_response.yaml"
        
        assert prompt_file.exists(), f"Missing {prompt_file}"
        
        registry = PromptRegistry()
        prompt = registry.load_from_yaml(prompt_file)
        
        assert prompt.name == "react_tool_response"
        assert "tool_name" in prompt.variables
        assert "tool_result" in prompt.variables

    def test_all_prompts_are_valid(self):
        """All prompt YAML files should pass validation."""
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        
        if not prompts_dir.exists():
            pytest.skip("Prompts directory not found")
        
        registry = PromptRegistry()
        registry.load_from_directory(prompts_dir)
        
        errors = registry.validate_all()
        
        assert errors == {}, f"Prompt validation errors: {errors}"

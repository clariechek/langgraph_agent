"""
Prompt management registry for versioned, validated prompts.

This module provides:
- YAML-based prompt definitions for easy editing
- Version tracking for prompt changes
- Variable validation to catch missing placeholders
- A central registry for all prompts

Usage:
    from src.prompts import PromptRegistry
    
    registry = PromptRegistry()
    prompt = registry.get("react_reasoning")
    formatted = prompt.format(tools="calculator", question="What is 2+2?")
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class PromptTemplate(BaseModel):
    """
    A prompt template with metadata and validation.
    
    Attributes:
        name: Unique identifier for the prompt
        version: Semantic version string (e.g., "1.0.0")
        description: Human-readable description
        template: The prompt text with {variable} placeholders
        variables: List of required variable names
    """

    name: str = Field(..., min_length=1)
    version: str = Field(default="1.0.0")
    description: str = Field(default="")
    template: str = Field(..., min_length=1)
    variables: list[str] = Field(default_factory=list)

    @field_validator("variables", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> list[str]:
        """Ensure variables is always a list."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)

    def format(self, **kwargs: Any) -> str:
        """
        Format the template with provided variables.
        
        Args:
            **kwargs: Variable values to substitute
        
        Returns:
            Formatted prompt string
        
        Raises:
            KeyError: If a required variable is missing
        """
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise KeyError(f"Missing required variables: {missing}")
        
        return self.template.format(**kwargs)

    def validate_variables(self) -> list[str]:
        """
        Check if template placeholders match declared variables.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Find all {variable} placeholders in template
        import re
        placeholders = set(re.findall(r"\{(\w+)\}", self.template))
        declared = set(self.variables)
        
        # Check for undeclared placeholders
        undeclared = placeholders - declared
        if undeclared:
            errors.append(f"Undeclared variables in template: {undeclared}")
        
        # Check for unused declared variables
        unused = declared - placeholders
        if unused:
            errors.append(f"Declared but unused variables: {unused}")
        
        return errors


class PromptRegistry:
    """
    Registry for loading and managing prompt templates.
    
    Prompts can be loaded from:
    - YAML files in a directory
    - Direct registration via code
    
    Example:
        registry = PromptRegistry()
        registry.load_from_directory("prompts/")
        prompt = registry.get("react_reasoning")
    """

    def __init__(self):
        self._prompts: dict[str, PromptTemplate] = {}

    def register(self, prompt: PromptTemplate) -> None:
        """
        Register a prompt template.
        
        Args:
            prompt: PromptTemplate instance to register
        """
        self._prompts[prompt.name] = prompt

    def get(self, name: str) -> PromptTemplate:
        """
        Get a prompt template by name.
        
        Args:
            name: Prompt name
        
        Returns:
            PromptTemplate instance
        
        Raises:
            KeyError: If prompt not found
        """
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found. Available: {list(self._prompts.keys())}")
        return self._prompts[name]

    def list_prompts(self) -> list[str]:
        """Get list of all registered prompt names."""
        return list(self._prompts.keys())

    def load_from_yaml(self, path: str | Path) -> PromptTemplate:
        """
        Load a prompt from a YAML file.
        
        Args:
            path: Path to YAML file
        
        Returns:
            Loaded PromptTemplate
        """
        path = Path(path)
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        prompt = PromptTemplate(**data)
        self.register(prompt)
        return prompt

    def load_from_directory(self, directory: str | Path) -> list[PromptTemplate]:
        """
        Load all YAML prompts from a directory.
        
        Args:
            directory: Path to directory containing .yaml files
        
        Returns:
            List of loaded PromptTemplates
        """
        directory = Path(directory)
        prompts = []
        
        for yaml_file in directory.glob("*.yaml"):
            prompt = self.load_from_yaml(yaml_file)
            prompts.append(prompt)
        
        return prompts

    def validate_all(self) -> dict[str, list[str]]:
        """
        Validate all registered prompts.
        
        Returns:
            Dict mapping prompt names to their validation errors
            (empty dict means all valid)
        """
        errors = {}
        for name, prompt in self._prompts.items():
            prompt_errors = prompt.validate_variables()
            if prompt_errors:
                errors[name] = prompt_errors
        return errors


# Global registry instance (can be imported directly)
_global_registry: PromptRegistry | None = None


def get_prompt_registry() -> PromptRegistry:
    """
    Get the global prompt registry.
    
    Creates the registry and loads default prompts on first call.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PromptRegistry()
        # Load default prompts if directory exists
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        if prompts_dir.exists():
            _global_registry.load_from_directory(prompts_dir)
    return _global_registry

"""Prompt management and registry."""

from src.prompts.registry import (
    PromptTemplate,
    PromptRegistry,
    get_prompt_registry,
)

__all__ = [
    "PromptTemplate",
    "PromptRegistry",
    "get_prompt_registry",
]

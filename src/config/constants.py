"""
Shared constants used across the application.

These values should rarely change and are not environment-specific.
For environment-specific configuration, use settings.py instead.
"""

# API Rate Limits
DEFAULT_RATE_LIMIT_REQUESTS = 100
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60

# LLM Defaults
DEFAULT_MAX_TOKENS = 4096
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY_SECONDS = 1.0
DEFAULT_RETRY_MULTIPLIER = 2.0  # Exponential backoff multiplier

# Agent Defaults
DEFAULT_MAX_ITERATIONS = 10
DEFAULT_TIMEOUT_SECONDS = 120

# Evaluation
DEFAULT_EVALUATION_THRESHOLD = 0.7
EVALUATION_METRICS = [
    "answer_relevancy",
    "faithfulness",
    "hallucination",
]

# Database
SUPPORTED_DB_DRIVERS = ["postgresql", "postgresql+asyncpg"]

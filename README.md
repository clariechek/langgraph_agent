# LangGraph Agent

Production-ready AI agent built with LangGraph, covering ReAct agents, tool creation, testing, and deployment patterns.

## Features

- **ReAct Agent**: Reasoning and acting agent with tool use
- **RAG Agent**: Retrieval-augmented generation for document Q&A
- **Chatbot**: Multi-turn conversation with memory
- **Multi-Agent**: Supervisor and parallel execution patterns

## Project Structure

```
langgraph_agent/
├── src/
│   ├── config/          # Environment and table configuration
│   ├── db/              # Database models and connections
│   ├── schemas/         # Pydantic schemas for LLM and DB
│   ├── prompts/         # Prompt templates and registry
│   ├── llm/             # LLM client wrappers
│   ├── tools/           # Agent tools
│   ├── agents/          # Agent implementations
│   └── evaluation/      # Evaluation and monitoring
├── tests/
│   ├── unit/            # Fast, isolated tests
│   ├── integration/     # Pipeline tests with mocks
│   └── evaluation/      # Semantic evaluation tests
└── prompts/             # YAML prompt templates
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (for production features)
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd langgraph_agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Running Tests

```bash
# Run all unit tests (fast)
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test markers
pytest -m unit -v
pytest -m integration -v
```

## Configuration

The project uses a layered configuration approach:

1. **Environment variables** (highest priority)
2. **`.env` file** (local development)
3. **Default values** (fallback)

See `.env.example` for available configuration options.

## Development

### Code Quality

```bash
# Format and lint
ruff check src/ tests/ --fix
ruff format src/ tests/

# Type checking
mypy src/
```

### Adding New Features

1. Create feature branch
2. Add implementation with tests
3. Run test suite
4. Submit PR

## License

MIT

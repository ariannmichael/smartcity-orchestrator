# Tests

This directory contains unit tests for the smartcity-orchestrator application.

## Structure

- `conftest.py` - Shared pytest fixtures and configuration
- `domain/` - Tests for domain layer (normalizers, rule evaluators, factories, registry)
- `application/` - Tests for application layer (event ingestion)
- `api/` - Tests for API routes and schemas
- `infra/` - Tests for infrastructure layer (outbox functionality)

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/domain/test_normalizers.py
```

Run specific test:
```bash
pytest tests/domain/test_normalizers.py::TestPydanticEventNormalizer::test_normalize_valid_energy_payload
```

## Test Coverage

The test suite covers:
- Event normalizers (Pydantic-based)
- Rule evaluators (Energy, Health, Noop, Passthrough)
- Factory classes (Energy, Health, Simple, Passthrough)
- Factory registry
- Event ingestion logic
- API routes (health, ingest, get_events)
- API schemas (IngestResponse, EventOut)
- Outbox notification enqueueing

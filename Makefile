.PHONY: help build up down restart logs shell migrate migrate-up migrate-down test test-watch clean

# Default target
help:
	@echo "Available targets:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all Docker services"
	@echo "  make down           - Stop all Docker services"
	@echo "  make restart        - Restart all Docker services"
	@echo "  make logs           - View logs from all services"
	@echo "  make shell          - Open shell in API container"
	@echo "  make migrate        - Run database migrations (upgrade to head)"
	@echo "  make migrate-up     - Run database migrations (upgrade to head)"
	@echo "  make migrate-down   - Rollback one migration"
	@echo "  make test           - Run all tests"
	@echo "  make test-watch     - Run tests in watch mode"
	@echo "  make clean          - Stop containers and remove volumes"

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Start all services and show logs
up-logs:
	docker-compose up

# Stop all services
down:
	docker-compose down

# Stop all services and remove volumes
down-volumes:
	docker-compose down -v

# Restart all services
restart: down up

# View logs from all services
logs:
	docker-compose logs -f

# View logs from specific service (usage: make logs-api, make logs-db, make logs-worker)
logs-api:
	docker-compose logs -f api

logs-db:
	docker-compose logs -f db

logs-worker:
	docker-compose logs -f worker

# Open shell in API container
shell:
	docker-compose exec api /bin/bash

# Run database migrations (upgrade to head)
migrate:
	docker-compose exec api alembic upgrade head

migrate-up:
	docker-compose exec api alembic upgrade head

# Rollback one migration
migrate-down:
	docker-compose exec api alembic downgrade -1

# Create a new migration (usage: make migrate-create MESSAGE="description")
migrate-create:
	docker-compose exec api alembic revision --autogenerate -m "$(MESSAGE)"

# Show current migration status
migrate-status:
	docker-compose exec api alembic current

# Show migration history
migrate-history:
	docker-compose exec api alembic history

# Run all tests
test:
	docker-compose exec api pytest

# Run tests with coverage
test-cov:
	docker-compose exec api pytest --cov=app --cov-report=html --cov-report=term

# Run tests in watch mode (requires pytest-watch, add to requirements if needed)
test-watch:
	docker-compose exec api ptw --runner "pytest"

# Run specific test file (usage: make test-file FILE=tests/api/test_routes.py)
test-file:
	docker-compose exec api pytest $(FILE)

# Run tests matching pattern (usage: make test-pattern PATTERN="test_ingest")
test-pattern:
	docker-compose exec api pytest -k $(PATTERN)

# Clean up: stop containers and remove volumes
clean: down-volumes

# Full setup: build, start services, and run migrations
setup: build up
	@echo "Waiting for database to be ready..."
	@sleep 5
	docker-compose exec api alembic upgrade head
	@echo "Setup complete! Services are running."

# Check service status
status:
	docker-compose ps

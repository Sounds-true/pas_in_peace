.PHONY: help install setup test lint format clean run docker-up docker-down migrate

# Colors for terminal output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)PAS Bot - Makefile Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Install dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	python -m spacy download ru_core_news_sm

setup: ## Initial setup (create venv, install deps, setup DB)
	@echo "$(GREEN)Setting up project...$(NC)"
	python3 -m venv venv
	@echo "$(YELLOW)Activate venv with: source venv/bin/activate$(NC)"
	@echo "$(YELLOW)Then run: make install$(NC)"

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	pytest -v

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linters (ruff, mypy)
	@echo "$(GREEN)Running linters...$(NC)"
	ruff check src/
	mypy src/

format: ## Format code with black and ruff
	@echo "$(GREEN)Formatting code...$(NC)"
	black src/ tests/
	ruff check src/ --fix

clean: ## Clean up cache and temporary files
	@echo "$(GREEN)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

run: ## Run the bot
	@echo "$(GREEN)Starting PAS Bot...$(NC)"
	python main.py

run-debug: ## Run the bot in debug mode
	@echo "$(GREEN)Starting PAS Bot in debug mode...$(NC)"
	LOG_LEVEL=DEBUG DEBUG=True python main.py

db-create: ## Create database
	@echo "$(GREEN)Creating database...$(NC)"
	createdb pas_bot || echo "Database may already exist"

db-drop: ## Drop database (WARNING: deletes all data)
	@echo "$(RED)Dropping database...$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		dropdb pas_bot; \
		echo "$(GREEN)Database dropped$(NC)"; \
	fi

migrate: ## Run database migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	alembic upgrade head

migrate-create: ## Create new migration
	@echo "$(GREEN)Creating new migration...$(NC)"
	@read -p "Migration name: " name; \
	alembic revision --autogenerate -m "$$name"

migrate-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	alembic downgrade -1

docker-up: ## Start Docker containers
	@echo "$(GREEN)Starting Docker containers...$(NC)"
	docker-compose up -d

docker-down: ## Stop Docker containers
	@echo "$(GREEN)Stopping Docker containers...$(NC)"
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f bot

docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker-compose build

docker-shell: ## Open shell in bot container
	docker-compose exec bot /bin/bash

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

psql: ## Open PostgreSQL CLI
	docker-compose exec postgres psql -U pas_user -d pas_bot

check-env: ## Check if .env file is configured
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file not found!$(NC)"; \
		echo "$(YELLOW)Run: cp .env.example .env$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN).env file found$(NC)"

check-deps: ## Check if all dependencies are installed
	@echo "$(GREEN)Checking dependencies...$(NC)"
	@python -c "import telegram; import langchain; import langgraph; import nemoguardrails" 2>/dev/null && \
		echo "$(GREEN)✓ Core dependencies installed$(NC)" || \
		echo "$(RED)✗ Core dependencies missing. Run: make install$(NC)"
	@python -c "import spacy; spacy.load('ru_core_news_sm')" 2>/dev/null && \
		echo "$(GREEN)✓ Russian language model installed$(NC)" || \
		echo "$(RED)✗ Russian model missing. Run: python -m spacy download ru_core_news_sm$(NC)"

status: check-env check-deps ## Check project status
	@echo ""
	@echo "$(GREEN)Project Status:$(NC)"
	@echo "Python: $$(python --version)"
	@echo "Environment: $$(grep ENVIRONMENT .env | cut -d= -f2)"
	@echo ""

dev-setup: setup install db-create migrate ## Complete development setup
	@echo ""
	@echo "$(GREEN)✓ Development environment ready!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate venv: $(YELLOW)source venv/bin/activate$(NC)"
	@echo "  2. Configure .env: $(YELLOW)cp .env.example .env && nano .env$(NC)"
	@echo "  3. Run bot: $(YELLOW)make run$(NC)"
	@echo ""

prod-deploy: ## Deploy to production (placeholder)
	@echo "$(YELLOW)Production deployment not yet implemented$(NC)"
	@echo "Use Docker Compose for now: make docker-up"
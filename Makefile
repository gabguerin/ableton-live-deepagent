.PHONY: help run dev start install clean lint test

.DEFAULT_GOAL := help

export PYTHONPATH := $(shell pwd)/src:$(PYTHONPATH)

help: ## Show this help message
	@echo "🎵 Ableton Producer Agent - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Launch Chainlit app with auto-reload and no auto-open
	@echo "🎵 Starting Ableton Producer Agent..."
	@echo "📝 Auto-reload: enabled"
	@echo "🌐 Browser auto-open: disabled"
	@echo "📍 App location: src/app.py"
	@echo ""
	uv run chainlit run src/app.py -w -h

dev: run ## Alias for 'run' - Launch app in development mode

start: ## Launch Chainlit app with auto-open (production-like)
	@echo "🎵 Starting Ableton Producer Agent (production mode)..."
	@echo "🌐 Browser will auto-open"
	@echo ""
	uv run chainlit run src/app.py

install: ## Install project dependencies
	@echo "📦 Installing dependencies..."
	uv sync

clean: ## Clean up temporary files and caches
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete

lint: ## Run code formatting and linting
	@echo "✨ Running code formatting..."
	uv run ruff check .
	uv run ruff format .

test: ## Run tests
	@echo "🧪 Running tests..."
	uv run pytest

init-env: ## Create .env file from example
	@if [ ! -f .env ]; then \
		if [ -f .env.example ]; then \
			cp .env.example .env; \
			echo "✅ Created .env file from .env.example"; \
		else \
			echo "❌ No .env.example file found"; \
		fi; \
	else \
		echo "⚠️  .env file already exists"; \
	fi
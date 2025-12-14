.PHONY: help run dev start install clean lint test

.DEFAULT_GOAL := help

export PYTHONPATH := $(shell pwd)/src:$(PYTHONPATH)

start: ## Launch Chainlit app with auto-open (production-like)
	@echo "🎵 Starting Ableton Producer Agent (production mode)..."
	@echo "🌐 Browser will auto-open"
	@echo ""
	uv run chainlit run src/app.py -h

install: ## Install project dependencies
	@echo "📦 Installing dependencies..."
	uv sync

.PHONY: help dev dev-api dev-web install db-up test

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' '{printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	cd apps/api && pip install -e .
	cd apps/web && npm install

dev: ## Start all services with Docker
	docker compose up --build

dev-api: ## Start API only (SQLite)
	cd apps/api && DATABASE_URL=sqlite+aiosqlite:///./isoclim.db uvicorn app.main:app --reload --port 8000

dev-web: ## Start web only
	cd apps/web && npm run dev

test: ## Run API tests
	cd apps/api && python -m pytest tests -v

db-up: ## Start PostgreSQL only
	docker compose up db

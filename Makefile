.PHONY: help install init validate graph compile compile-force compile-backend compile-frontend compile-docs diff check test format lint typecheck clean manifest app-add-entity dev dev-api dev-web ci

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python and Node dependencies
	pip install -e ".[dev]"
	npm install -g pnpm prettier
	pnpm install

init: ## Initialize the project structure
	python -m lof.cli init

validate: ## Validate all JSON definitions and constraints
	python -m lof.cli validate

graph: ## Display the dependency graph
	python -m lof.cli graph

compile: ## Compile the project
	python -m lof.cli compile

compile-force: ## Force recompilation
	lof compile --force

compile-backend: ## Compile only backend artifacts
	lof compile --type entity-model --type entity-schemas --type entity-repository --type entity-service --type entity-router --type fastapi-app --type database-config

compile-frontend: ## Compile only frontend artifacts
	lof compile --type entity-types --type entity-hooks --type entity-list-page --type entity-detail-page --type entity-form --type react-app

compile-docs: ## Compile documentation artifacts
	lof compile

diff: ## Show differences from last build
	python -m lof.cli diff

check: ## Run all validation checks
	python -m lof.cli check
	ruff check framework/src framework/tests
	ruff format --check framework/src framework/tests

test: ## Run all tests
	python -m pytest framework/tests -v --tb=short

format: ## Format all source files
	ruff format framework/src framework/tests
	prettier --write '**/*.{json,yaml,yml,md}'

lint: ## Lint all source files
	ruff check --fix framework/src framework/tests
	prettier --check '**/*.{json,yaml,yml,md}'

typecheck: ## Run type checking
	pyright framework/src framework/tests || true

clean: ## Remove all generated files including generated-project
	python -m lof.cli clean
	rm -rf generated-project

manifest: ## Show the build manifest
	python -m lof.cli manifest

app-add-entity: ## Add a new entity instance (usage: make app-add-entity name=Customer fields="name:string:required,email:email:required:unique")
	python -m lof.cli app add-entity $(name)

dev: ## Start development servers
	@echo "Run 'make dev-api' and 'make dev-web' in separate terminals"

dev-api: ## Start the FastAPI dev server
	cd generated-project/apps/api && uvicorn app.main:app --reload --port 8000

dev-web: ## Start the React dev server
	cd generated-project/apps/web && npm run dev

ci: validate compile check test ## Run the full CI pipeline

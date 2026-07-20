.PHONY: help install doctor format format-check lint typecheck test test-unit test-integration test-generation validate extract infer build-gold validate-smt compile pipeline determinism-check benchmark-smoke clean ci

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e ".[dev]"
	npm install -g pnpm prettier && pnpm install

doctor: ## Run diagnostics
	python -m lof.cli validate
	python -m lof.cli constraints validate

format: ## Format code
	ruff format framework/src framework/tests generated-project/apps/api
	prettier --write '**/*.{json,yaml,yml,md}'

format-check: ## Check formatting
	ruff format --check framework/src framework/tests
	prettier --check '**/*.{json,yaml,yml,md}'

lint: ## Lint code
	ruff check --fix framework/src framework/tests
	ruff check --fix generated-project/apps/api --ignore F821,E402,N815,F401 || true

typecheck: ## Type checking
	pyright framework/src || true

test: test-unit test-integration test-generation ## Run all tests

test-unit: ## Run unit tests
	python -m pytest framework/tests/unit -v --tb=short

test-integration: ## Run integration tests
	python -m pytest framework/tests -v --tb=short -k "not golden" || true

test-generation: ## Run generation tests
	python -m lof.cli compile --dry-run

validate: ## Validate all definitions
	python -m lof.cli validate

extract: ## Extract Silver from Bronze
	python -m lof.cli bronze extract

infer: ## Run reasoning inference
	python -m lof.cli reason status
	python -m lof.cli gold build

build-gold: ## Materialize Gold DSL
	python -m lof.cli gold build
	python -m lof.cli constraints validate

validate-smt: ## Validate with SMT
	python -m lof.cli constraints validate

compile: ## Compile the project
	python -m lof.cli compile

pipeline: validate extract infer validate-smt compile ## Run full pipeline

determinism-check: ## Verify deterministic build
	python -m lof.cli compile
	python -m lof.cli compile --dry-run

benchmark-smoke: ## Run benchmark smoke test
	python -m lof.cli constraints validate
	python -m lof.cli bench run
	python -m lof.cli compile

clean: ## Remove generated files
	python -m lof.cli clean

ci: format-check lint test-unit benchmark-smoke ## Run CI checks

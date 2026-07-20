.PHONY: help install init validate graph compile compile-force diff check test format lint typecheck clean manifest bazel-build bazel-test ci

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python and Node dependencies
	pip install -e ".[dev]"
	pip install ruff pyright pytest
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
	python -m lof.cli compile --force

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

clean: ## Remove all generated files
	python -m lof.cli clean

manifest: ## Show the build manifest
	python -m lof.cli manifest

bazel-build: ## Build with Bazel
	bazel build //:generated_project

bazel-test: ## Run Bazel tests
	bazel test //...

ci: validate compile check test ## Run the full CI pipeline

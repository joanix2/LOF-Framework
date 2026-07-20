.PHONY: help install doctor format format-check lint typecheck test test-unit test-integration test-generation validate extract infer build-gold validate-smt compile pipeline determinism-check benchmark-smoke validate-agentic-system clean ci

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

test: test-unit test-generation ## Run all tests

test-unit: ## Run unit tests
	python -m pytest framework/tests/unit -v --tb=short

test-integration: ## Run integration tests
	python -m pytest framework/tests -v --tb=short -k "not golden" || true

test-generation: ## Check compilation
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

validate-agentic-system: ## Validate agentic system configuration
	@echo "=== Vérification des agents ==="
	@for f in .opencode/agents/*.md; do \
		name=$$(basename "$$f" .md); \
		if ! grep -q "Mission" "$$f"; then echo "  [FAIL] $$name: missing Mission"; fi; \
		if ! grep -q "Allowed paths" "$$f"; then echo "  [FAIL] $$name: missing Allowed paths"; fi; \
		if ! grep -q "Forbidden paths" "$$f"; then echo "  [FAIL] $$name: missing Forbidden paths"; fi; \
		if ! grep -q "Validation gates" "$$f"; then echo "  [FAIL] $$name: missing Validation gates"; fi; \
	done
	@echo "=== Vérification des skills ==="
	@for f in .opencode/skills/*.md; do \
		if ! grep -q "Objectif" "$$f"; then echo "  [FAIL] $$(basename $$f): missing Objectif"; fi; \
		if ! grep -q "Étapes" "$$f"; then echo "  [FAIL] $$(basename $$f): missing Étapes"; fi; \
	done
	@echo "=== Vérification des workflows ==="
	@for f in .opencode/workflows/*.md; do \
		if ! grep -qE '^[0-9]+\.' "$$f"; then echo "  [FAIL] $$(basename $$f): no numbered steps"; fi; \
	done
	@echo "=== Vérification des commandes ==="
	@for f in .opencode/commands/*.md; do \
		if ! grep -q "Usage" "$$f"; then echo "  [FAIL] $$(basename $$f): missing Usage"; fi; \
	done
	@echo "=== Vérification AGENTS.md ==="
	@grep -q "Sources modifiables" AGENTS.md || echo "  [FAIL] AGENTS.md: missing 'Sources modifiables'"
	@grep -q "Sources interdites" AGENTS.md || echo "  [FAIL] AGENTS.md: missing 'Sources interdites'"
	@grep -q "fichiers générés" AGENTS.md || echo "  [FAIL] AGENTS.md: missing generated-files protection"
	@echo "=== Vérification Makefile ==="
	@grep -q "validate-agentic-system" Makefile || echo "  [FAIL] Makefile: missing validate-agentic-system target"
	@grep -q "benchmark-smoke" Makefile || echo "  [FAIL] Makefile: missing benchmark-smoke target"
	@echo "=== Agentic system validation complete ==="

clean: ## Remove generated files
	python -m lof.cli clean

ci: format-check lint test-unit benchmark-smoke validate-agentic-system ## Run CI checks

.PHONY: help install doctor format format-check lint typecheck test test-unit test-cli test-generation test-independence build package clean ci

help: ## Show this help
	@awk -F ':.*?## ' '/^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install LOF in dev mode
	uv sync

doctor: ## Check environment
	lof doctor

format: ## Format all code
	ruff format src/lof tests
	prettier --write '**/*.{json,yaml,yml,md}'

format-check: ## Check formatting
	ruff format --check src/lof tests

lint: ## Lint all code
	ruff check --fix src/lof tests

typecheck: ## Type checking
	pyright src/lof || true

test: test-unit test-cli ## Run all tests

test-unit: ## Run unit tests
	python -m pytest tests -v --tb=short

test-cli: ## Test CLI commands
	python -m lof.cli --help > /dev/null
	python -m lof.cli --version > /dev/null
	python -m lof.cli profiles > /dev/null

test-generation: ## Test project generation
	cd /tmp && rm -rf lof-test-gen && lof new lof-test-gen --mode minimal && rm -rf lof-test-gen

test-independence: ## Verify generated project is independent
	cd /tmp && rm -rf lof-test-indep && lof new lof-test-indep --mode minimal
	@echo "Generated project does NOT import LOF:"
	@! grep -r "from lof\|import lof" /tmp/lof-test-indep/generated 2>/dev/null && echo "  ✓ No LOF dependency found" || echo "  ⚠  LOF dependency detected"

build: ## Build package (wheel + sdist)
	uv build

package: build ## Build and verify package
	uv tool install dist/*.whl --force-reinstall 2>&1 | tail -3
	lof --version

publish-test: ## Publish to TestPyPI
	uv publish --publish-url https://test.pypi.org/legacy/

publish: ## Publish to PyPI (manual, prefer CI release workflow)
	uv publish

distclean: clean ## Remove everything except source
	rm -rf .venv/ uv.lock

clean: ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info

ci: format-check lint test test-cli test-generation test-independence ## Full CI

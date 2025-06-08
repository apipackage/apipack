# APIpack Makefile
# Development and deployment automation

.PHONY: help install install-dev test test-cov lint format type-check build clean docs serve-docs release

# Default target
help:
	@echo "APIpack Development Commands"
	@echo "============================="
	@echo ""
	@echo "Setup:"
	@echo "  install      Install package in production mode"
	@echo "  install-dev  Install package in development mode with all dependencies"
	@echo "  setup-ollama Setup Ollama with Mistral model"
	@echo ""
	@echo "Development:"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run linting (flake8, mypy)"
	@echo "  format       Format code (black, isort)"
	@echo "  type-check   Run type checking (mypy)"
	@echo ""
	@echo "Examples:"
	@echo "  examples     Generate example packages"
	@echo "  test-examples Test example packages"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Build documentation"
	@echo "  serve-docs   Serve documentation locally"
	@echo ""
	@echo "Release:"
	@echo "  build        Build package distribution"
	@echo "  clean        Clean build artifacts"
	@echo "  release      Release to PyPI"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs,test,all]"
	pre-commit install

setup-ollama:
	@echo "Setting up Ollama with Mistral model..."
	@if ! command -v ollama &> /dev/null; then \
		echo "Installing Ollama..."; \
		curl -fsSL https://ollama.ai/install.sh | sh; \
	fi
	@echo "Pulling Mistral 7B model..."
	ollama pull mistral:7b
	@echo "Starting Ollama server..."
	ollama serve &
	@echo "Ollama setup complete!"

# Testing targets
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=apipack --cov-report=html --cov-report=term-missing

test-integration:
	pytest tests/integration/ -v --slow

test-e2e:
	pytest tests/e2e/ -v --slow

# Code quality targets
lint:
	flake8 apipack tests
	mypy apipack

format:
	black apipack tests
	isort apipack tests

type-check:
	mypy apipack --strict

check-all: lint type-check test

# Example targets
examples:
	@echo "Generating example packages..."
	cd examples/pdf2text && apipack generate config.yml --output ../../generated/pdf2text
	cd examples/html2pdf && apipack generate config.yml --output ../../generated/html2pdf
	cd examples/image-resize && apipack generate config.yml --output ../../generated/image-resize

test-examples: examples
	@echo "Testing generated examples..."
	cd generated/pdf2text && python -m pytest tests/ -v
	cd generated/html2pdf && npm test
	cd generated/image-resize && go test ./...

build-examples: examples
	@echo "Building example Docker images..."
	cd generated/pdf2text && docker build -t apipack/pdf2text .
	cd generated/html2pdf && docker build -t apipack/html2pdf .
	cd generated/image-resize && docker build -t apipack/image-resize .

# Documentation targets
docs:
	cd docs && make html

serve-docs:
	cd docs/_build/html && python -m http.server 8000

docs-clean:
	cd docs && make clean

# Build and release targets
build: clean
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

release: build
	python -m twine upload dist/*

# Development utilities
install-pre-commit:
	pre-commit install
	pre-commit install --hook-type commit-msg

run-pre-commit:
	pre-commit run --all-files

# Local development server
dev-server:
	@echo "Starting development environment..."
	@echo "Starting Ollama server..."
	ollama serve &
	@echo "Ollama server started on http://localhost:11434"

# Performance testing
perf-test:
	cd tests/performance && python benchmark.py

# Security scanning
security-scan:
	bandit -r apipack/
	safety check

# Docker development
docker-build:
	docker build -t apipack:dev .

docker-test: docker-build
	docker run --rm apipack:dev pytest tests/

# Database migrations (if needed in future)
migrate:
	@echo "No migrations needed yet"

# Monitoring and health checks
health-check:
	apipack health

# Template validation
validate-templates:
	python scripts/validate_templates.py

# Generated package testing
test-generated-packages:
	@echo "Testing all generated packages..."
	find generated/ -name "test_*.py" -exec python -m pytest {} \;

# CLI testing
test-cli:
	@echo "Testing CLI commands..."
	apipack --help
	apipack health
	apipack templates
	apipack config

# Comprehensive test suite
test-all: test test-integration test-examples test-cli
	@echo "All tests completed!"

# Development workflow
dev-workflow: install-dev format lint type-check test
	@echo "Development workflow completed successfully!"

# CI/CD simulation
ci: format lint type-check test-cov test-integration
	@echo "CI pipeline simulation completed!"

# Package validation
validate-package: build
	python -m twine check dist/*

# Dependency updates
update-deps:
	pip-compile requirements.in
	pip-compile requirements-dev.in

# Version bump utilities
bump-patch:
	bumpversion patch

bump-minor:
	bumpversion minor

bump-major:
	bumpversion major

# Cleanup generated files
clean-generated:
	rm -rf generated/
	mkdir -p generated

# Reset development environment
reset-dev: clean clean-generated
	pip uninstall apipack -y
	$(MAKE) install-dev

# Performance profiling
profile:
	python -m cProfile -o profile.stats scripts/profile_generation.py
	python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumtime').print_stats(20)"

# Memory profiling
memory-profile:
	python -m memory_profiler scripts/profile_generation.py

# Benchmark comparisons
benchmark:
	python scripts/benchmark_languages.py
	python scripts/benchmark_interfaces.py

# Quick development checks
quick-check: format lint
	@echo "Quick development checks passed!"

# Full release preparation
prepare-release: clean format lint type-check test-all docs build validate-package
	@echo "Release preparation completed!"
	@echo "Ready to run: make release"
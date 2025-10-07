# Makefile for CulicidaeLab Server Documentation

.PHONY: help docs docs-build docs-serve docs-clean docs-validate docs-links docs-deploy

# Default target
help:
	@echo "Available documentation commands:"
	@echo "  docs-build     Build documentation"
	@echo "  docs-serve     Build and serve documentation locally"
	@echo "  docs-clean     Clean build artifacts"
	@echo "  docs-validate  Validate documentation content"
	@echo "  docs-links     Check documentation links"
	@echo "  docs-deploy    Build and deploy documentation"
	@echo "  docs-dev       Development build with auto-reload"
	@echo ""
	@echo "Examples:"
	@echo "  make docs-serve    # Start local development server"
	@echo "  make docs-build    # Build production documentation"
	@echo "  make docs-validate # Validate content before building"

# Build documentation
docs-build:
	@echo "🚀 Building documentation..."
	uv run python scripts/build_docs.py

# Build and serve documentation locally
docs-serve:
	@echo "🌐 Starting documentation server..."
	uv run mkdocs serve

# Development build with auto-reload
docs-dev:
	@echo "🔄 Starting development server with auto-reload..."
	uv run mkdocs serve --dev-addr=127.0.0.1:8000

# Clean build artifacts
docs-clean:
	@echo "🧹 Cleaning documentation build artifacts..."
	rm -rf site/
	rm -rf .mkdocs_cache/
	rm -rf docs/.cache/

# Validate documentation content
docs-validate:
	@echo "🔍 Validating documentation content..."
	uv run python scripts/validate_docs.py

# Check documentation links
docs-links:
	@echo "🔗 Checking documentation links..."
	uv run mkdocs build --quiet
	uv run python scripts/check_links.py

# Build and deploy documentation (for CI/CD)
docs-deploy:
	@echo "🚀 Building and deploying documentation..."
	uv run python scripts/build_docs.py --clean
	@echo "✅ Documentation ready for deployment"

# Full documentation workflow (validate, build, check)
docs-full: docs-validate docs-build docs-links
	@echo "✅ Full documentation workflow completed"

# Install documentation dependencies
docs-install:
	@echo "📦 Installing documentation dependencies..."
	uv sync --group docs

# Update pre-commit hooks
docs-setup:
	@echo "⚙️  Setting up documentation tools..."
	uv sync --group docs
	pre-commit install
	@echo "✅ Documentation tools setup complete"
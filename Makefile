.PHONY: help test test-unit test-tools test-integration lint format clean install

# Default target
help:
	@echo "ONI Save Parser - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests (unit + tools + integration)"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-tools        - Test all tools on sample saves"
	@echo "  make test-integration  - Run integration tests on test saves"
	@echo "  make test-fast         - Run quick tests (unit + small saves)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint              - Run linters (ruff)"
	@echo "  make format            - Auto-format code (ruff format)"
	@echo "  make typecheck         - Run mypy type checking"
	@echo ""
	@echo "Tools Demo:"
	@echo "  make demo-basic        - Demo basic_usage.py"
	@echo "  make demo-geyser       - Demo geyser_info.py"
	@echo "  make demo-duplicant    - Demo duplicant_info.py"
	@echo "  make demo-scanner      - Demo colony_scanner.py"
	@echo "  make demo-resources    - Demo resource_counter.py"
	@echo "  make demo-all          - Run all demos"
	@echo ""
	@echo "Development:"
	@echo "  make install           - Install dependencies with uv"
	@echo "  make clean             - Remove temporary files"
	@echo ""

# Installation
install:
	uv sync

# Run all tests
test: test-unit test-tools test-integration

# Run unit tests
test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/unit/ -v

# Test all tools on sample saves (fast)
test-tools:
	@echo "Testing all tools on sample saves..."
	@echo ""
	@echo "=== Testing basic_usage.py ==="
	uv run python examples/basic_usage.py test_saves/02-mid-game-cycle-148.sav
	@echo ""
	@echo "=== Testing geyser_info.py ==="
	uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav
	@echo ""
	@echo "=== Testing duplicant_info.py ==="
	uv run python examples/duplicant_info.py test_saves/02-mid-game-cycle-148.sav
	@echo ""
	@echo "=== Testing colony_scanner.py ==="
	uv run python examples/colony_scanner.py test_saves --no-recursive
	@echo ""
	@echo "=== Testing resource_counter.py ==="
	uv run python examples/resource_counter.py test_saves/02-mid-game-cycle-148.sav --list-elements
	@echo ""
	@echo "✓ All tools completed successfully!"

# Run integration tests on test saves
test-integration:
	@echo "Running integration tests on test saves..."
	uv run pytest tests/ -v -k "not unit"

# Fast tests (unit + small save only)
test-fast: test-unit
	@echo ""
	@echo "Quick tool verification on small save..."
	uv run python examples/resource_counter.py test_saves/01-early-game-cycle-010.sav --list-elements
	@echo "✓ Fast tests completed!"

# Linting
lint:
	@echo "Running ruff linter..."
	uv run ruff check src/ examples/ tests/

# Format code
format:
	@echo "Formatting code with ruff..."
	uv run ruff format src/ examples/ tests/
	@echo "✓ Code formatted!"

# Type checking
typecheck:
	@echo "Running mypy type checker..."
	uv run mypy src/ examples/

# Demo tools
demo-basic:
	@echo "=== Basic Usage Demo (mid-game save) ==="
	uv run python examples/basic_usage.py test_saves/02-mid-game-cycle-148.sav

demo-geyser:
	@echo "=== Geyser Info Demo (mid-game save) ==="
	uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav

demo-duplicant:
	@echo "=== Duplicant Info Demo (mid-game save) ==="
	uv run python examples/duplicant_info.py test_saves/02-mid-game-cycle-148.sav

demo-scanner:
	@echo "=== Colony Scanner Demo (mid-game save) ==="
	uv run python examples/colony_scanner.py test_saves/02-mid-game-cycle-148.sav --no-recursive

demo-resources:
	@echo "=== Resource Counter Demo (mid-game save) ==="
	uv run python examples/resource_counter.py test_saves/02-mid-game-cycle-148.sav

demo-all: demo-basic demo-geyser demo-duplicant demo-scanner demo-resources
	@echo ""
	@echo "✓ All demos completed!"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	find . -type d -name "*.egg-info" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "tmp_*.py" -delete
	@echo "✓ Cleanup complete!"

# Performance benchmarking
benchmark:
	@echo "Benchmarking parser on different save sizes..."
	@echo ""
	@echo "Small (0.8 MB, cycle 10):"
	@time uv run python -c "from oni_save_parser import load_save_file; load_save_file('test_saves/01-early-game-cycle-010.sav')"
	@echo ""
	@echo "Medium (2.2 MB, cycle 148):"
	@time uv run python -c "from oni_save_parser import load_save_file; load_save_file('test_saves/02-mid-game-cycle-148.sav')"
	@echo ""
	@echo "Large (12.5 MB, cycle 1160):"
	@time uv run python -c "from oni_save_parser import load_save_file; load_save_file('test_saves/03-late-game-cycle-1160.sav')"
	@echo ""
	@echo "Very Large (29.2 MB, cycle 1434):"
	@time uv run python -c "from oni_save_parser import load_save_file; load_save_file('test_saves/04-advanced-cycle-1434.sav')"

# Quick resource count on all test saves
test-resources-all:
	@echo "Testing resource_counter on all test saves..."
	@for save in test_saves/*.sav; do \
		echo ""; \
		echo "=== $$save ==="; \
		uv run python examples/resource_counter.py "$$save" --list-elements; \
	done

# CI/CD targets
ci-test: test-unit test-fast
	@echo "✓ CI tests passed!"

ci-full: lint test
	@echo "✓ Full CI passed!"

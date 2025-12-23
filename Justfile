# Requires: just, uv, Python 3.14.2 (non-free-threaded build)
# All tasks use uv to ensure isolated, reproducible runs.
# NOTE: Using non-free-threaded due to Python 3.14 doctest recursion bug (see conftest.py)

# Default recipe shows help
default:
    @just --list

# Print environment info
info:
    @echo "Python: $(python --version)"
    @uv --version

# Install project and dev dependencies
install:
    uv sync --all-groups

# Alias for install (better discoverability)
setup: install

# Run tests (sequential)
test *ARGS:
    uv run pytest {{ ARGS }}

# Run tests (parallel)
test-parallel *ARGS:
    uv run pytest -n auto {{ ARGS }}

# Run tests with free-threading safety checks (parallel threads + iterations)
test-freethreaded *ARGS:
    uv run pytest --threads=8 --iterations=10 --require-gil-disabled {{ ARGS }}

# Lint code (check for issues)
lint *ARGS:
    uv run ruff check {{ ARGS }} .

# Format code (auto-format)
fmt *ARGS:
    uv run ruff format {{ ARGS }} .

# Check formatting without modifying files (for CI)
fmt-check *ARGS:
    uv run ruff format --check {{ ARGS }} .

# Lint and auto-fix
lint-fix:
    uv run ruff check --fix .

# Type checking
typecheck *ARGS:
    PYTHONPATH=examples uv run ty check {{ ARGS }}

# Build docs
docs:
    uv run sphinx-build -b html docs docs/_build/html

# Build docs with auto-reload for development
docs-live:
    uv run sphinx-autobuild docs docs/_build/html

# Clean docs build
docs-clean:
    rm -rf docs/_build

# Build docs and open in browser
docs-open:
    just docs && open docs/_build/html/index.html

# Build docs with all checks
docs-checks:
    just docs && just lint && just fmt-check

# Build sdist/wheel
build:
    uv build

# Clean build and cache artifacts
clean:
    rm -rf .pytest_cache .ruff_cache .pyright .mypy_cache build dist
    find docs/_build -mindepth 1 -maxdepth 1 -not -name ".gitkeep" -exec rm -rf {} + || true

# Run all quality checks with fail-fast behavior
ci-checks:
    just install && just lint && just fmt-check && just typecheck && just test

# Run all checks + free-threading safety tests
ci-checks-ft:
    just ci-checks && just test-freethreaded

# Enable pre-push hook to run ci-checks before pushing
enable-pre-push:
    @echo "Installing pre-push hook..."
    @echo '#!/bin/sh' > .git/hooks/pre-push
    @echo '' >> .git/hooks/pre-push
    @echo '# Run quality checks before push' >> .git/hooks/pre-push
    @echo 'echo "Running quality checks before push..."' >> .git/hooks/pre-push
    @echo 'if ! just ci-checks; then' >> .git/hooks/pre-push
    @echo '    echo "Pre-push check failed! Push aborted."' >> .git/hooks/pre-push
    @echo '    exit 1' >> .git/hooks/pre-push
    @echo 'fi' >> .git/hooks/pre-push
    @chmod +x .git/hooks/pre-push
    @echo "Pre-push hook installed! Use 'just disable-pre-push' to disable."

# Disable pre-push hook
disable-pre-push:
    @chmod -x .git/hooks/pre-push 2>/dev/null || true
    @echo "Pre-push hook disabled. Use 'just enable-pre-push' to re-enable."

# Run slow tests (marked with @pytest.mark.slow)
test-slow *ARGS:
    uv run pytest -m slow {{ ARGS }}

# Run doctest examples via Sybil integration with pytest
# WARNING: Python 3.14 has recursion bug in error formatting (see conftest.py)
test-doctest *ARGS:
    uv run pytest src/ {{ ARGS }}

# Run doctest examples in docs/ and README.md
test-docs *ARGS:
    uv run pytest docs/ README.md {{ ARGS }}

# Run all doctests (src + docs + README)
test-all-doctests *ARGS:
    uv run pytest src/ docs/ README.md {{ ARGS }}

# Run performance benchmark
benchmark:
    uv run python -m tdom_path.profiling.benchmark

# Profile tree transformation operations
profile:
    uv run python -m tdom_path.profiling.profiler

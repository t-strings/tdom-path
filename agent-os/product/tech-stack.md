# Tech Stack

## Language & Runtime
- **Language:** Python 3.14+ (free-threaded support targeted)
- **Package Manager:** uv (modern Python package installer and resolver)
- **Build System:** pyproject.toml with PEP 517/518 compliant build backend

## Core Dependencies
- **tdom:** Node-based rendering framework (core dependency for Node structure and rendering lifecycle)
- **t-strings:** Template strings (PEP 750 compatible template literal support for Python)
- **pathlib:** PurePath interface for type-safe path operations (standard library)
- **typing:** Protocols and type hints for pluggable architecture (standard library)

## Testing & Quality
- **Test Framework:** pytest with 100% coverage target
- **Test Structure:** Unit tests in `tests/` directory, fixture tests for test fixtures
- **Coverage:** Focus on essential tests avoiding over-testing, but aim for complete coverage
- **Type Checking:** mypy or pyright for static type validation
- **Linting/Formatting:** ruff or similar Python linter for code quality

## Framework Integration Support
- **Dynamic Frameworks:** Flask, Django, FastAPI (integration helpers, not hard dependencies)
- **Static Site Generators:** Sphinx, Pelican (integration helpers, not hard dependencies)
- **Integration Pattern:** Protocol-based pluggable architecture allowing framework-specific resolvers

## Development Tools
- **IDE Support:** Type hints and actual file paths designed for PyCharm, VS Code, and other Python IDEs
- **Static Analysis:** Support for pylint, mypy, and other static analysis tools to validate paths
- **CLI Tooling:** Command-line utilities for path validation and asset manifest generation

## Architecture Patterns
- **Context Management:** ChainMap pattern for immutable system context + mutable per-render state
- **Path Resolution:** PurePath interface with custom implementations
- **Plugin System:** Protocol-based service architecture for extensibility
- **Node Processing:** Direct Node structure manipulation avoiding parse/stringify cycles
- **Lifecycle Hooks:** Before/after render hooks in context object

## Design Constraints
- **Framework Portable:** No hard dependencies on specific web frameworks
- **Tooling Friendly:** Declarative patterns that support static analysis
- **Performance Oriented:** Single-pass processing, caching, free-threading friendly
- **Type Safe:** Comprehensive type hints for IDE support and static checking

## Future Considerations
- **Free-Threading:** Designed for compatibility with Python 3.13+ free-threaded mode
- **Build System Integration:** Hooks for asset optimization pipelines (bundlers, minifiers)
- **Caching:** Potential Redis/disk caching for resolved paths in production environments
- **Monitoring:** Integration points for performance monitoring and error tracking

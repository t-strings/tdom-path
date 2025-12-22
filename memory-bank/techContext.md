# Technical Context: tdom-path

## Technology Stack
*   **Language**: Python 3.14+ (targeted for free-threading support).
*   **Package Manager**: `uv` for modern dependency management and environment isolation.
*   **Core UI Library**: `tdom` for Node-based rendering and tree structures.
*   **Template Strings**: `t-strings` (PEP 750/771) for first-class template literal support.
*   **Path Operations**: Standard library `pathlib.PurePath` and `importlib.resources`.
*   **Type Safety**: Comprehensive PEP 484/585/604/695 type hints. Verified with `mypy` or `pyright`.
*   **Automation**: `just` as the task runner for formatting, linting, and testing.

## Core Architecture Concepts
*   **Node-Based Transformation**: Unlike string-based templating, `tdom-path` walks the `tdom` Node tree and replaces path strings with resolved objects or relative paths directly in the elements.
*   **Protocol-Based Abstraction**: Pluggable architecture using Python Protocols to allow framework-specific path resolution (e.g., `RelativePathStrategy`).
*   **Lifecycle Integration**: Path resolution can occur at:
    *   **Definition Time**: When a component is created.
    *   **Application Time**: During a live request.
    *   **Build Time**: During static site generation.

## Technical Constraints & Standards
*   **Framework Agnostic**: No hard dependencies on Django, Flask, or FastAPI.
*   **Free-Threading Friendly**: Data structures (like the render context) are designed to be immutable or thread-safe for Python 3.13+ free-threaded mode.
*   **Zero-Overhead Parsing**: By using `tdom` Nodes, we avoid the overhead of parsing HTML strings to find paths.
*   **100% Test Coverage**: High-priority target for all core functionality.

## Development Workflow
1.  **Iterate**: Implement features in `src/tdom_path/`.
2.  **Format**: `just fmt` (using `ruff`).
3.  **Lint**: `just lint-fix`.
4.  **Check**: `just typecheck`.
5.  **Test**: `just test` (using `pytest`).

## Deployment & Distribution
*   **Standards Compliant**: Uses `pyproject.toml` with PEP 517/518 build backend.
*   **Package-Ready**: Designed to resolve assets correctly when installed via wheels using `importlib.resources`.

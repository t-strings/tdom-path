# System Patterns: tdom-path

## Core Architecture Patterns

### 1. Node-Based Path Rewriting
Instead of manipulating HTML strings, `tdom-path` operates on the `tdom` Node tree. This is more efficient and allows for richer metadata preservation.
*   **Tree Walker**: A function that traverses the Node tree looking for elements that need path resolution (e.g., `<link>`, `<script>`, `<img>`).
*   **Transformation**: The walker replaces plain string paths with `PurePosixPath` instances or fully resolved relative/absolute URLs depending on the strategy.

### 2. The `@path_nodes` Decorator
A high-level pattern for component integration. Decorating a component (or its render method) allows `tdom-path` to automatically process its assets during the `tdom` rendering lifecycle.

### 3. TraversableElement Pattern
To support `PurePosixPath` and other complex types in element attributes (which `tdom` usually restricts to strings/bools), we use the `TraversableElement` subclass.
*   **Purpose**: Holds path objects that will be rendered into strings at the final stage.
*   **Switching**: The tree walker converts standard `Element` nodes to `TraversableElement` when a path needs to be stored.

### 4. Strategy Pattern for Resolution
Path resolution is delegated to strategy objects (e.g., `RelativePathStrategy`).
*   **Protocols**: Define the interface for path resolvers.
*   **Pluggability**: Allows the same component tree to be rendered differently for local development (relative paths) vs. production (CDN URLs) vs. SSG (absolute paths with site prefix).

### 5. Render Context with ChainMap
Separates immutable system-level configuration from mutable per-render state.
*   **ChainMap**: Efficiently stacks contexts.
*   **Performance**: Minimizes copying while ensuring thread safety for concurrent rendering (free-threading support).

## Coding Standards & Patterns
*   **Keyword-Only Arguments**: Component functions use `*` to force keyword arguments for clarity and easier refactoring.
*   **Dataclass Components**: Components are typically implemented as dataclasses for clean state management and automatic `__init__` generation.
*   **Modern Python Types**: Aggressive use of `|` for unions and built-in generics (e.g., `list[str]`).
*   **Absolute Imports**: used throughout the `src/` layout.

## Package Resource Pattern
Leveraging `importlib.resources.files` to treat package data as a filesystem.
*   **Module-Relative Paths**: `make_path(component, asset)` uses the component's module to find its static files.
*   **Handle Repeated Module Names**: Logic to handle `package.module.module` structure commonly found in some Python layouts.

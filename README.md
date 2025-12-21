# tdom-path

Component resource path utilities for web applications using importlib.resources

## Overview

`tdom-path` provides utilities for resolving component static assets (CSS, JS, images) in component-based
web applications. It uses `importlib.resources` for proper package data access that works with both
development directories and installed packages (wheels).

## Features

- **Component Asset Resolution:** Pass component classes/instances directly to resolve static assets
- **Tree Rewriting:** Automatically transform `<link>` and `<script>` elements to use Traversable paths
- **Decorator Support:** Use `@path_nodes` decorator for automatic tree transformation
- **importlib.resources Integration:** Uses `importlib.resources.files()` for proper package resolution
- **Works with Wheels:** Static assets work in installed packages, not just src/ development mode
- **Filesystem Operations:** Returned paths support `.exists()`, `.read_text()`, `.is_file()`, etc.
- **Type Safety:** Comprehensive type hints with IDE autocomplete and type checking support
- **Simple API:** Clean functions for both manual and automatic use cases

## Installation

```bash
uv pip install tdom-path
```

## Quick Start

### Basic Path Resolution

```python
from tdom_path import make_path
from mysite.components.heading import Heading

# Get path to component's static asset
css_path = make_path(Heading, "static/styles.css")

# Returns Traversable with filesystem operations
print(css_path)  # /path/to/mysite/components/heading/static/styles.css
print(css_path.exists())  # True
print(css_path.is_file())  # True

# Read the file content
content = css_path.read_text()
print(content)  # /* CSS content */

# Works with component instances too
heading = Heading("Welcome")
js_path = make_path(heading, "static/script.js")
```

### Tree Rewriting with Decorator

```python
from tdom import Element
from tdom_path import path_nodes

class Heading:
    @path_nodes
    def __html__(self):
        # Just write string paths, decorator handles transformation
        return Element("html", children=[
            Element("head", children=[
                Element("link", {"rel": "stylesheet", "href": "static/styles.css"}),
                Element("script", {"src": "static/script.js"}),
            ]),
            Element("body", children=[
                Element("h1", children=["Hello World"]),
            ]),
        ])

# When __html__() is called, link href and script src are automatically
# transformed to Traversable objects using make_path()
heading = Heading()
html_tree = heading.__html__()
```

### Manual Tree Rewriting

```python
from tdom import Element
from tdom_path import make_path_nodes
from mysite.components.heading import Heading

# Create tree with string asset references
tree = Element("html", children=[
    Element("head", children=[
        Element("link", {"rel": "stylesheet", "href": "static/styles.css"}),
        Element("script", {"src": "static/script.js"}),
    ]),
])

# Transform tree to use Traversable
new_tree = make_path_nodes(tree, Heading)
# new_tree now has Traversable objects in link href and script src attributes
```

## Integration with importlib.resources

`make_path` uses `importlib.resources.files()` under the hood, which means it works seamlessly
with Python's package resource system:

```python
from importlib.resources import files
from mysite.components.heading import Heading

# These are equivalent:
# 1. Using make_path (recommended)
from tdom_path import make_path
css_path = make_path(Heading, "static/styles.css")

# 2. Using importlib.resources directly
package_path = files("mysite.components.heading")
css_path = package_path / "static/styles.css"
```

## Tree Rewriting

The tree rewriting functionality walks a tdom Node tree and automatically detects elements with static asset references (`<link>` and `<script>` tags), converting their `href`/`src` attribute values from strings to Traversable objects.

### What Gets Transformed

- `<link>` tags with `href` attribute (anywhere in tree)
- `<script>` tags with `src` attribute (anywhere in tree)

### What Gets Skipped

External URLs and special schemes are left unchanged:
- External URLs: `http://`, `https://`, `//`
- Special schemes: `mailto:`, `tel:`, `data:`, `javascript:`
- Anchor-only links: `#...`

### Using the Decorator

The `@path_nodes` decorator supports both function components and class component methods:

```python
from tdom_path import path_nodes

# Function component
@path_nodes
def heading(text: str):
    return Element("link", {"href": "static/styles.css"})

# Class component with __call__
class Heading:
    @path_nodes
    def __call__(self):
        return Element("link", {"href": "static/styles.css"})

# Class component with __html__
class Heading:
    @path_nodes
    def __html__(self):
        return Element("link", {"href": "static/styles.css"})
```

### Mixed External and Local Assets

```python
@path_nodes
def page():
    return Element("head", children=[
        # External CSS - not transformed
        Element("link", {
            "rel": "stylesheet",
            "href": "https://cdn.example.com/style.css"
        }),
        # Local CSS - transformed to Traversable
        Element("link", {
            "rel": "stylesheet",
            "href": "static/styles.css"
        }),
    ])
```

## API Reference

### make_path

```python
def make_path(component: Any, asset: str) -> Traversable
```

Create path to component asset using importlib.resources.

**Parameters:**
- `component`: Python object with `__module__` attribute (class, function, instance, etc.)
- `asset`: Relative path to the asset within the component package (e.g., `"static/styles.css"`)

**Returns:**
- `Traversable` path object with filesystem operations (`.exists()`, `.read_text()`, `.is_file()`, etc.)

**Raises:**
- `TypeError`: If component doesn't have `__module__` attribute

**Examples:**
```python
# Get CSS file
css_path = make_path(Heading, "static/styles.css")

# Get JavaScript file
js_path = make_path(Heading, "static/script.js")

# Get image in subdirectory
img_path = make_path(Heading, "static/images/logo.png")

# Check if file exists
if css_path.exists():
    content = css_path.read_text()
```

### make_path_nodes

```python
def make_path_nodes(target: Node, component: Any) -> Node
```

Rewrite asset-bearing attributes in a tdom tree to use make_path.

Walks the Node tree and detects elements with static asset references (`<link>` and `<script>` tags), converting their `href`/`src` string attributes to Traversable using `make_path(component, attr_value)`.

**Parameters:**
- `target`: Root node of the tree to process
- `component`: Component instance/class for make_path() resolution

**Returns:**
- New Node tree with asset attributes converted to Traversable (immutable transformation)

**Examples:**
```python
from tdom import Element
from mysite.components.heading import Heading

# Create tree with string references
tree = Element("head", children=[
    Element("link", {"rel": "stylesheet", "href": "static/styles.css"})
])

# Transform to use Traversable
new_tree = make_path_nodes(tree, Heading)
```

### path_nodes

```python
@path_nodes
```

Decorator to automatically apply make_path_nodes to component output.

Supports both function components and class component methods. For function components, uses the function itself as the component. For class methods (`__call__` or `__html__`), uses self as the component.

**Examples:**
```python
# Function component
@path_nodes
def heading(text: str) -> Element:
    return Element("link", {"href": "static/styles.css"})

# Class component
class Heading:
    @path_nodes
    def __html__(self) -> Element:
        return Element("link", {"href": "static/styles.css"})
```

## Development Status

**Current Phase:** Phase 2 - Tree Rewriting (Complete)

### Phase 1 - Core Path API (Complete)

- ✅ `make_path()` function for component asset resolution
- ✅ Uses `importlib.resources.files()` for package resolution
- ✅ Returns `Traversable` with full filesystem operations
- ✅ Handles repeated module names (e.g., `heading.heading` → `heading`)
- ✅ Works with classes, instances, and any object with `__module__`
- ✅ Type safe with comprehensive type hints
- ✅ 5 focused tests covering core functionality
- ✅ 100% test coverage on webpath.py
- ✅ ty type checker compliance

### Phase 2 - Tree Rewriting (Complete)

- ✅ `make_path_nodes()` function for tree transformation
- ✅ `@path_nodes` decorator for automatic transformation
- ✅ Supports both function and class components
- ✅ Detects `<link>` tags anywhere in tree
- ✅ Detects `<script>` tags anywhere in tree
- ✅ Skips external URLs and special schemes
- ✅ Immutable tree transformation (creates new tree)
- ✅ 12 comprehensive tests
- ✅ 96% test coverage on tree.py
- ✅ Type safe with ty compliance

### Design Decisions

- **Simple API:** Direct functions instead of class-based API
- **Direct Returns:** Returns `Traversable` directly (not `PurePosixPath`) for filesystem operations
- **Component-centric:** Pass component objects directly, framework extracts `__module__`
- **Immutable Transformations:** Tree rewriting creates new nodes, doesn't mutate originals
- **Decorator Pattern:** Optional decorator for convenience, function always available for explicit use
- **Python 3.14+:** No `from __future__ import annotations` needed

## Requirements

- Python 3.14+
- tdom >= 0.1.13

## Testing

```bash
# Run tests
just test

# Run tests in parallel
just test-parallel

# Run all quality checks (lint, format, typecheck, test)
just ci-checks

# Type checking with ty
just typecheck
```

## Design Philosophy

1. **Simple and Focused:** Direct function APIs for resolving component assets
2. **Use Standard Library:** Leverage `importlib.resources` for package resolution
3. **Works with Wheels:** Component assets work in installed packages, not just development mode
4. **Filesystem Operations:** Return objects with real filesystem capabilities
5. **Component-centric:** Pass component objects directly, framework extracts `__module__`
6. **Type Safety First:** Comprehensive type hints enable excellent IDE support
7. **Immutable by Default:** Tree transformations create new structures
8. **Keep It Simple:** No complex policies or abstractions - direct path resolution only

## License

[Add license information]

## Contributing

[Add contribution guidelines]

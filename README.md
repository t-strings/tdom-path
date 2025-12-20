# tdom-path

Component resource path utilities for web applications using importlib.resources

## Overview

`tdom-path` provides utilities for resolving component static assets (CSS, JS, images) in component-based
web applications. It uses `importlib.resources` for proper package data access that works with both
development directories and installed packages (wheels).

## Features

- **Component Asset Resolution:** Pass component classes/instances directly to resolve static assets
- **importlib.resources Integration:** Uses `importlib.resources.files()` for proper package resolution
- **Works with Wheels:** Static assets work in installed packages, not just src/ development mode
- **Filesystem Operations:** Returned paths support `.exists()`, `.read_text()`, `.is_file()`, etc.
- **Type Safety:** Comprehensive type hints with IDE autocomplete and type checking support
- **Simple API:** Single function `make_path(component, asset)` for all use cases

## Installation

```bash
uv pip install tdom-path
```

## Quick Start

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

## Development Status

**Current Phase:** Phase 1 - Core Path API (Complete)

### Completed

- ✅ `make_path()` function for component asset resolution
- ✅ Uses `importlib.resources.files()` for package resolution
- ✅ Returns `Traversable` with full filesystem operations
- ✅ Handles repeated module names (e.g., `heading.heading` → `heading`)
- ✅ Works with classes, instances, and any object with `__module__`
- ✅ Type safe with comprehensive type hints
- ✅ 5 focused tests covering core functionality
- ✅ 100% test coverage
- ✅ ty type checker compliance

### Design Decisions

- **Simple API:** Single function instead of class-based API
- **Direct Returns:** Returns `Traversable` directly (not `PurePosixPath`) for filesystem operations
- **Component-centric:** Pass component objects directly, not string paths
- **No URL Policies:** Removed index.html/trailing slash policies - keep it simple
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

1. **Simple and Focused:** Single function API for resolving component assets
2. **Use Standard Library:** Leverage `importlib.resources` for package resolution
3. **Works with Wheels:** Component assets work in installed packages, not just development mode
4. **Filesystem Operations:** Return objects with real filesystem capabilities
5. **Component-centric:** Pass component objects directly, framework extracts `__module__`
6. **Type Safety First:** Comprehensive type hints enable excellent IDE support
7. **Keep It Simple:** No complex policies or abstractions - direct path resolution only

## License

[Add license information]

## Contributing

[Add contribution guidelines]

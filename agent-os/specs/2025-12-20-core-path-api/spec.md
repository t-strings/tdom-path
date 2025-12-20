# Specification: Core Path API

## Goal

Create a simple utility function that enables component static asset resolution using `importlib.resources`, working
with both development directories and installed packages (wheels).

## User Stories

- As a component author, I want to pass my component class to get paths to static assets (CSS, JS, images)
- As a package maintainer, I want component assets to work when installed as wheels, not just in src/ development mode
- As a developer, I want filesystem operations (`.exists()`, `.read_text()`, `.is_file()`) on returned paths

## Specific Requirements

**Simple Function API**

- Single function `make_path(component, asset)` for all use cases
- Takes a component object (class, instance, any object with `__module__`)
- Takes an asset path string (e.g., `"static/styles.css"`)
- Returns `Traversable` object from `importlib.resources`
- No class-based API, no complex abstractions

**Component Module Extraction**

- Extract `__module__` attribute from component object
- Handle repeated module names: `mysite.components.heading.heading` → `mysite.components.heading`
- Raise `TypeError` if object doesn't have `__module__` attribute
- Works with classes, instances, functions, or any object with `__module__`

**Package Resource Integration**

- Uses `importlib.resources.files()` for package resolution
- Returns `Traversable` objects with filesystem operations
- Works with installed packages (wheels, zip files) not just src/ development
- Cross-platform compatible (Windows, Unix)

**Filesystem Operations**

- Returned `Traversable` supports:
    - `.exists()` - Check if file/directory exists
    - `.is_file()` - Check if it's a file
    - `.is_dir()` - Check if it's a directory
    - `.read_text()` - Read file contents as text
    - `.read_bytes()` - Read binary contents
    - String conversion via `str(path)`

**Type Hints and IDE Integration**

- Return type: `Traversable` from `importlib.resources.abc`
- Comprehensive type hints on all parameters
- Support ty type checker (Python 3.14+)
- No need for `from __future__ import annotations`

**Testing Strategy with 100% Coverage**

- Test basic functionality with component classes
- Test with component instances
- Test different asset paths (CSS, JS, images in subdirectories)
- Test error handling for objects without `__module__`
- Test filesystem operations (`.exists()`, `.is_file()`, `.read_text()`)
- Use real example component in tests (not mocked)

## Design Decisions

**Simplicity Over Features**

- No URL policy parameters (index.html, trailing slash, etc.)
- No relative path calculation (removed `relative_path` function)
- No package notation string conversion (removed `WebPath` class)
- Just one focused function: resolve component asset to filesystem path

**Return Type Choice**

- Return `Traversable` directly (not `PurePosixPath`)
- Preserves filesystem operations that `importlib.resources` provides
- More capabilities than `PurePosixPath` which is path-manipulation only

**API Design**

- Function-based, not class-based
- Component-centric: pass objects, not string paths
- Asset path is explicit second parameter

## Implementation

**File: `src/tdom_path/webpath.py`**

```python
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import Any


def make_path(component: Any, asset: str) -> Traversable:
    """Create path to component asset using importlib.resources."""
    # Extract __module__ from component
    if not hasattr(component, "__module__"):
        raise TypeError(f"Object {component!r} has no __module__ attribute")

    module_name = component.__module__

    # Handle repeated module names (e.g., heading.heading -> heading)
    parts = module_name.split(".")
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        module_name = ".".join(parts[:-1])

    # Use importlib.resources to get package location
    package_path = files(module_name)

    # Join asset path and return
    return package_path / asset
```

**File: `src/tdom_path/__init__.py`**

```python
from tdom_path.webpath import make_path

__all__ = ["make_path"]
```

## Example Usage

```python
from tdom_path import make_path
from mysite.components.heading import Heading

# Get path to CSS file
css_path = make_path(Heading, "static/styles.css")

# Use filesystem operations
if css_path.exists():
    content = css_path.read_text()
    print(f"Found CSS with {len(content)} characters")

# Works with instances too
heading = Heading("Welcome")
js_path = make_path(heading, "static/script.js")
```

## Out of Scope

- URL policy handling (index.html, trailing slash, etc.)
- Relative path calculation between components
- Package notation string conversion (dots to slashes)
- Class-based API with path manipulation methods
- Context objects or dependency injection
- Framework integrations
- Tree rewriting and middleware patterns
- Build-time optimizations
- Caching or memoization

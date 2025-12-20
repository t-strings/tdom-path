# Task Breakdown: Core Path API

## Overview

**Status:** ✅ Complete

Total Task Groups: 1 (simplified from original 6-group plan)
Focus: Simple function API for component asset resolution using importlib.resources

## Completed Tasks

### Task Group 1: Component Asset Resolution Function

**Dependencies:** None

- [x] 1.0 Complete component asset resolution implementation
    - [x] 1.1 Write focused tests for make_path() function
        - Test basic functionality with component classes
        - Test with component instances
        - Test different asset paths (CSS, JS, images in subdirectories)
        - Test error handling for objects without `__module__`
        - Test filesystem operations (`.exists()`, `.is_file()`, `.read_text()`)
        - Total: 5 tests achieving 100% coverage
    - [x] 1.2 Create make_path() function using importlib.resources
        - Accept component object (any object with `__module__` attribute)
        - Accept asset path string (e.g., `"static/styles.css"`)
        - Extract `__module__` from component
        - Handle repeated module names: `heading.heading` → `heading`
        - Use `importlib.resources.files()` for package resolution
        - Return `Traversable` object directly (not `PurePosixPath`)
    - [x] 1.3 Add type hints with Traversable return type
        - Import `Traversable` from `importlib.resources.abc`
        - Type hint component parameter as `Any`
        - Type hint asset parameter as `str`
        - Return type: `Traversable` (not `PurePosixPath`)
        - No need for `from __future__ import annotations` (Python 3.14+)
    - [x] 1.4 Implement component module extraction
        - Check if component has `__module__` attribute
        - Raise `TypeError` if missing with clear message
        - Split module name on dots
        - Strip last component if it repeats the second-to-last
        - Example: `mysite.components.heading.heading` → `mysite.components.heading`
    - [x] 1.5 Create example component for testing
        - Create `examples/mysite/components/heading/` package structure
        - Add `Heading` component class with `__html__()` method
        - Create `static/styles.css` file with sample CSS
        - Configure pytest to add `examples` to PYTHONPATH
        - Tests import real component, not mocked
    - [x] 1.6 Ensure all tests pass with 100% coverage
        - Run pytest: all 5 tests pass
        - Check coverage: 100% for `src/tdom_path/`
        - Type checking: ty passes
        - Linting: ruff passes
        - Formatting: ruff format passes

**Acceptance Criteria:**

- ✅ All 5 tests pass
- ✅ 100% test coverage achieved
- ✅ Returns `Traversable` with filesystem operations (not `PurePosixPath`)
- ✅ Works with component classes and instances
- ✅ Handles repeated module names correctly
- ✅ Type checking passes (ty)
- ✅ Real example component used in tests

## Design Decisions Made

**Simplified from Original Plan:**

The original plan had 6 task groups with complex features:
1. Path Class Foundation (WebPath class)
2. Relative Path Algorithm (relative_to override)
3. Filesystem Integration (validation)
4. Edge Case Handling (anchors, special chars)
5. Protocol Definitions (extensibility)
6. Comprehensive Testing

**Final Implementation:**

We simplified to a single function API:
- **Single function:** `make_path(component, asset)` replaces class-based API
- **Direct return:** Returns `Traversable` directly (not converted to `PurePosixPath`)
- **No URL policies:** Removed index.html, trailing slash logic
- **No relative paths:** Removed relative path calculation between components
- **No validation:** Trust `importlib.resources` to handle package resolution
- **Simple testing:** 5 focused tests instead of 20-50 tests

**Why Traversable Instead of PurePosixPath?**

`Traversable` is better because:
- Has filesystem operations: `.exists()`, `.is_file()`, `.is_dir()`, `.read_text()`, `.read_bytes()`
- `PurePosixPath` is path-manipulation only (no filesystem access)
- `importlib.resources.files()` returns `Traversable` natively
- Converting to `PurePosixPath` loses functionality
- Cross-platform compatible (Windows and Unix)

## Implementation Summary

**File: `src/tdom_path/webpath.py`** (13 lines of code)

```python
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import Any

def make_path(component: Any, asset: str) -> Traversable:
    if not hasattr(component, "__module__"):
        raise TypeError(f"Object {component!r} has no __module__ attribute")

    module_name = component.__module__
    parts = module_name.split(".")
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        module_name = ".".join(parts[:-1])

    package_path = files(module_name)
    return package_path / asset
```

**File: `src/tdom_path/__init__.py`** (2 lines of code)

```python
from tdom_path.webpath import make_path
__all__ = ["make_path"]
```

**File: `tests/test_webpath.py`** (5 tests)

1. `test_make_path_basic()` - Basic functionality, returns Traversable
2. `test_make_path_file_exists()` - Filesystem operations work
3. `test_make_path_component_instance()` - Works with instances
4. `test_make_path_different_assets()` - Multiple asset types
5. `test_make_path_no_module_attribute()` - Error handling

## Out of Scope (Removed from Original Plan)

The following were in the original plan but removed for simplicity:

- **Task Group 2-6:** All removed (relative paths, validation, edge cases, protocols, comprehensive testing)
- **WebPath class:** Function-based API instead
- **PurePosixPath wrapping:** Return Traversable directly
- **Relative path calculation:** Out of scope
- **URL policy handling:** Out of scope (index.html, trailing slash)
- **Path validation logic:** Trust importlib.resources
- **Protocol definitions:** Keep it simple
- **Cross-platform tests:** Traversable handles it
- **Parameterized tests:** 5 simple tests sufficient

## Key Metrics

- **Lines of code:** 15 (implementation)
- **Test count:** 5
- **Test coverage:** 100%
- **Cyclomatic complexity:** Low (simple linear function)
- **Dependencies:** Only stdlib (`importlib.resources`, `typing`)

## Future Phases

If future phases need more features, they can be added incrementally:
- Phase 2: Could add relative path calculation if needed
- Phase 3: Could add context objects if needed
- Phase 4: Could add validation if needed

For now, the simple single-function API meets the core requirement: resolve component static assets using importlib.resources.

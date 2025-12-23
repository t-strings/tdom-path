# tdom-path

Component resource path utilities for web applications using Traversable paths

## Overview

`tdom-path` provides utilities for resolving component static assets (CSS, JS, images) in component-based
web applications. It supports both package assets (using `package:path` syntax) and relative paths,
returning `Traversable` objects that represent resource locations suitable for web rendering.

## Features

- **Package Asset Support:** Reference assets from installed packages using `package:asset/path` syntax
- **Component Asset Resolution:** Pass component classes/instances directly to resolve local assets
- **Tree Rewriting:** Automatically transform `<link>` and `<script>` elements to use Traversable
- **Decorator Support:** Use `@path_nodes` decorator for automatic tree transformation
- **Flexible Path Formats:** Supports package paths, relative paths with `./` or `../`, and plain paths
- **Cross-Platform:** Traversable ensures consistent resource access across platforms
- **Type Safety:** Comprehensive type hints with IDE autocomplete and type checking support
- **Asset Validation:** Automatic validation that referenced assets exist (fail-fast with clear errors)
- **Simple API:** Clean functions for both manual and automatic use cases

## Installation

```bash
uv add install tdom-path
```

## Quick Start

### Package Asset Support

Reference assets from installed Python packages using the `package:path` syntax:

```python
from tdom_path import make_path

# Reference asset from an installed package
# Format: "package_name:resource/path"
css_path = make_path(None, "mypackage:static/styles.css")

# Returns Traversable pointing to the package resource
print(css_path)  # Traversable instance
print(css_path.is_file())  # True if the file exists

# Use in HTML templates with package paths
from tdom import html

tree = html(t'''
    <head>
        <link rel="stylesheet" href="mypackage:static/styles.css">
        <script src="mypackage:static/app.js"></script>
    </head>
''')
```

**How Path Type Detection Works:**

- If the path contains a colon (`:`), it's treated as a package path
- Otherwise, it's treated as a relative path (relative to the component's module)
- No need to specify the type explicitly - detection is automatic

### Relative Path Support

Reference assets relative to your component's location:

```python
from tdom_path import make_path
from mysite.components.heading import Heading

# Relative path (plain format)
css_path = make_path(Heading, "static/styles.css")

# Relative path with ./ prefix (explicit current directory)
css_path = make_path(Heading, "./static/styles.css")

# Relative path with ../ prefix (parent directory)
shared_path = make_path(Heading, "../shared/common.css")

# Returns Traversable pointing to the component's module resource
print(css_path)  # Traversable instance
```

**Supported Relative Path Formats:**

- `static/styles.css` - Plain relative path
- `./static/styles.css` - Explicit current directory
- `../shared/utils.css` - Parent directory navigation

### Basic Path Resolution

```python
from tdom_path import make_path
from mysite.components.heading import Heading

# Get path to component's static asset (relative path)
css_path = make_path(Heading, "static/styles.css")

# Returns Traversable with resource location
print(type(css_path))  # <class 'importlib.resources.abc.Traversable'>

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
        # Mix package paths and relative paths
        return Element("html", children=[
            Element("head", children=[
                # Package asset
                Element("link", {"rel": "stylesheet", "href": "bootstrap:dist/css/bootstrap.css"}),
                # Local component asset
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

# Create tree with string asset references (mix package and relative paths)
tree = Element("html", children=[
    Element("head", children=[
        # Package path - references asset from installed package
        Element("link", {"rel": "stylesheet", "href": "mypackage:static/base.css"}),
        # Relative path - references local component asset
        Element("link", {"rel": "stylesheet", "href": "static/styles.css"}),
        Element("script", {"src": "static/script.js"}),
    ]),
])

# Transform tree to use Traversable
new_tree = make_path_nodes(tree, Heading)
# new_tree now has Traversable objects in link href and script src attributes
```

## Path Syntax Reference

### Package Paths

Use the `package:path` syntax to reference assets from installed Python packages:

```python
# Basic syntax: "package_name:resource/path"
"mypackage:static/styles.css"  # Asset from mypackage
"bootstrap:dist/css/bootstrap.css"  # Asset from bootstrap package
"my.package:images/logo.png"  # Asset from my.package (dotted names supported)

# The component parameter is ignored for package paths
make_path(None, "mypackage:static/styles.css")  # component=None is fine
make_path(Heading, "mypackage:static/styles.css")  # component is ignored
```

**Package Path Detection:**

- Any path containing a colon (`:`) is treated as a package path
- Package name is extracted from the left side of the colon
- Resource path is extracted from the right side of the colon

### Relative Paths

Reference assets relative to the component's module location:

```python
# Plain relative path (no prefix)
"static/styles.css"

# Explicit current directory
"./static/styles.css"

# Parent directory navigation
"../shared/utils.css"

# All require a component with __module__ attribute
make_path(Heading, "static/styles.css")  # Uses Heading's module location
```

**Relative Path Detection:**

- Any path *without* a colon (`:`) is treated as a relative path
- Resolved relative to the component's `__module__` location
- Component parameter is required (must have `__module__` attribute)

## Asset Validation

All asset paths are automatically validated during tree transformation:

```python
from tdom_path import make_path_nodes

# If an asset doesn't exist, transformation fails immediately
tree = html(t'''
    <head>
        <link rel="stylesheet" href="mypackage:static/missing.css">
    </head>
''')

try:
    make_path_nodes(tree, Heading)
except FileNotFoundError as e:
    # Error message includes:
    # - Asset filename
    # - Attribute name (href/src)
    # - Component context
    # - Full path for debugging
    print(e)  # "Asset not found: 'missing.css' (attribute: 'href', component: 'Heading'...)"
```

**Validation Features:**

- Fail-fast: Errors raised immediately when asset not found
- Clear error messages with full context
- Includes component and attribute information for debugging

**Future Validation Options (TODO):**

The current implementation uses immediate failure. Future versions may support:
- Batch mode: Collect all missing assets and report at end
- Strict/lenient modes: Configurable behavior via flags
- Warning mode: Log warnings instead of failing
- Configurable validation strategies

## Tree Rewriting

The tree rewriting functionality walks a tdom Node tree and automatically detects elements with static asset references (`<link>` and `<script>` tags), converting their `href`/`src` attribute values from strings to Traversable objects.

### What Gets Transformed

- `<link>` tags with `href` attribute (anywhere in tree)
- `<script>` tags with `src` attribute (anywhere in tree)
- Both package paths and relative paths are transformed

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
        # Package CSS - transformed to Traversable
        Element("link", {
            "rel": "stylesheet",
            "href": "bootstrap:dist/css/bootstrap.css"
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

Create path to asset resource as a Traversable instance.

Supports two path formats:

1. **Package paths:** `"package:resource/path"` (e.g., `"mypackage:static/styles.css"`)
   - Resolves using `importlib.resources.files()` to access package resources
   - Works with any installed package
   - Component parameter is ignored for package paths

2. **Relative paths:** `"resource/path"` or `"./resource/path"` or `"../resource/path"`
   - Resolves relative to the component's module
   - Uses the component's `__module__` attribute to determine the base location
   - Component parameter is required (must have `__module__`)

Path type detection is automatic based on presence of colon (`:`) character.

**Parameters:**
- `component`: Python object with `__module__` attribute (class, function, instance, etc.)
              For package paths, this parameter is ignored and can be None.
- `asset`: Path to the asset. Can be:
          - Package path: `"package:resource/path"`
          - Relative path: `"resource/path"`, `"./resource/path"`, or `"../resource/path"`

**Returns:**
- `Traversable` instance representing the resource location

**Raises:**
- `TypeError`: If component doesn't have `__module__` attribute (relative paths only)
- `ModuleNotFoundError`: If a package path references a non-existent package
- `ImportError`: If there's an issue importing a package

**Examples:**
```python
# Package path - access asset from installed package
pkg_path = make_path(None, "mypackage:static/styles.css")

# Relative path - access local component asset
css_path = make_path(Heading, "static/styles.css")

# With ./ prefix
css_path = make_path(Heading, "./static/styles.css")

# Parent directory
shared_path = make_path(Heading, "../shared/common.css")
```

### make_path_nodes

```python
def make_path_nodes(target: Node, component: Any) -> Node
```

Rewrite asset-bearing attributes in a tdom tree to use make_path.

Walks the Node tree and detects elements with static asset references (`<link>` and `<script>` tags), converting their `href`/`src` string attributes to Traversable using `make_path(component, attr_value)`.

Automatically validates that all assets exist, raising FileNotFoundError immediately if any asset is not found.

**Parameters:**
- `target`: Root node of the tree to process
- `component`: Component instance/class for make_path() resolution (used for relative paths only)

**Returns:**
- New Node tree with asset attributes converted to Traversable (immutable transformation)

**Raises:**
- `FileNotFoundError`: If any referenced asset doesn't exist
- `ModuleNotFoundError`: If a package path references a non-existent package

**Examples:**
```python
from tdom import Element
from mysite.components.heading import Heading

# Create tree with mixed package and relative paths
tree = Element("head", children=[
    Element("link", {"rel": "stylesheet", "href": "bootstrap:dist/css/bootstrap.css"}),
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
    return Element("link", {"href": "mypackage:static/styles.css"})

# Class component
class Heading:
    @path_nodes
    def __html__(self) -> Element:
        return Element("link", {"href": "static/styles.css"})
```

### render_path_nodes

```python
def render_path_nodes(
    tree: Node,
    target: PurePosixPath,
    strategy: RenderStrategy | None = None
) -> Node
```

Render TraversableElement nodes to Element nodes with relative path strings.

Walks the Node tree, detects TraversableElement instances containing Traversable attribute values, and transforms them into regular Element instances with those paths rendered as strings using the provided strategy.

This is the final rendering step after `make_path_nodes()` has converted asset paths to Traversable instances. It calculates the appropriate string representation for each path based on the target output location.

**Parameters:**
- `tree`: Root node of the tree to process
- `target`: PurePosixPath target output location (e.g., `"mysite/pages/index.html"`)
- `strategy`: Optional RenderStrategy for path calculation. Defaults to `RelativePathStrategy()` if None.

**Returns:**
- New Node tree with TraversableElement nodes transformed to Element nodes containing string path attributes

**Examples:**
```python
from pathlib import PurePosixPath
from tdom import html
from tdom_path import make_path_nodes, render_path_nodes
from tdom_path.tree import RelativePathStrategy
from mysite.components.heading import Heading

# Step 1: Create tree with string asset paths
tree = html(t'''
    <head>
        <link rel="stylesheet" href="mypackage:static/styles.css">
    </head>
''')

# Step 2: Transform to TraversableElement with Traversable
path_tree = make_path_nodes(tree, Heading)

# Step 3: Render to Element with relative path strings
target = PurePosixPath("mysite/pages/about.html")
rendered = render_path_nodes(path_tree, target)

# With site prefix for subdirectory deployment
strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
rendered = render_path_nodes(path_tree, target, strategy=strategy)
```

### RelativePathStrategy

```python
@dataclass(frozen=True, slots=True)
class RelativePathStrategy:
    site_prefix: PurePosixPath | None = None
```

Strategy for rendering paths as relative URLs.

Calculates relative paths from the target output location to the source asset location, optionally prepending a site prefix for deployment scenarios where assets are served from a subdirectory.

**Parameters:**
- `site_prefix`: Optional PurePosixPath prefix to prepend to all calculated paths (e.g., `PurePosixPath("mysite/static")`)

**Examples:**
```python
from pathlib import PurePosixPath
from tdom_path.tree import RelativePathStrategy
from tdom_path.webpath import make_path
from mysite.components.heading import Heading

# Basic relative path calculation
strategy = RelativePathStrategy()
source = make_path(Heading, "static/styles.css")
target = PurePosixPath("mysite/pages/about.html")
path_str = strategy.calculate_path(source, target)

# With site prefix for subdirectory deployment
strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
path_str = strategy.calculate_path(source, target)
```

### RenderStrategy Protocol

```python
class RenderStrategy(Protocol):
    def calculate_path(self, source: Traversable, target: PurePosixPath) -> str:
        ...
```

Protocol for path rendering strategies.

Defines the interface for calculating how Traversable paths should be rendered as strings in the final HTML output. Implementations can provide different rendering strategies such as relative paths, absolute paths, CDN URLs, etc.

**Extensibility:**
Create custom strategies by implementing the protocol:

```python
from pathlib import PurePosixPath
from importlib.resources.abc import Traversable
from tdom_path.tree import RenderStrategy

class AbsolutePathStrategy:
    """Render all paths as absolute URLs."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def calculate_path(self, source: Traversable, target: PurePosixPath) -> str:
        return f"{self.base_url}/{source}"

# Use custom strategy
strategy = AbsolutePathStrategy("https://cdn.example.com")
rendered = render_path_nodes(path_tree, target, strategy=strategy)
```

## Full Pipeline Example

Here's a complete example showing the full pipeline from component to rendered HTML:

```python
from pathlib import PurePosixPath
from tdom import html
from tdom_path import make_path_nodes, render_path_nodes
from tdom_path.tree import RelativePathStrategy
from mysite.components.heading import Heading

# 1. Define your component with mixed package and relative paths
class Heading:
    def __html__(self):
        return html(t'''
            <div class="heading">
                <link rel="stylesheet" href="bootstrap:dist/css/bootstrap.css">
                <link rel="stylesheet" href="static/heading.css">
                <script src="static/heading.js"></script>
                <h1>Welcome</h1>
            </div>
        ''')

# 2. Transform string paths to Traversable (package and component-relative)
heading = Heading()
tree = heading.__html__()
path_tree = make_path_nodes(tree, heading)
# Bootstrap link href is now: Traversable for bootstrap package
# Heading link href is now: Traversable for component's static/heading.css
# Script src is now: Traversable for component's static/heading.js

# 3. Render for a specific target page (relative paths)
target = PurePosixPath("mysite/pages/about.html")
rendered_tree = render_path_nodes(path_tree, target)
# Paths are now calculated relative to target location

# 4. Convert to HTML string
html_output = str(rendered_tree)
```

## Migration Guide

### From PurePosixPath to Traversable

The library now uses `Traversable` as the primary return type instead of `PurePosixPath`. This change enables first-class support for package assets and better represents the resource-oriented nature of path resolution.

**What Changed:**

- `make_path()` now returns `Traversable` instead of `PurePosixPath`
- TraversableElement attrs now accept `Traversable` instead of `PurePosixPath`
- RenderStrategy protocol now accepts `Traversable` source parameter

**Backward Compatibility:**

The change is largely transparent for most use cases:

```python
# Old code (still works with Traversable)
css_path = make_path(Heading, "static/styles.css")
print(str(css_path))  # Still works - Traversable converts to string

# New feature - package paths
pkg_path = make_path(None, "mypackage:static/styles.css")
print(pkg_path.is_file())  # Traversable provides file operations
```

**When Migration is Needed:**

If your code explicitly checks for `PurePosixPath` type:

```python
# Old code
if isinstance(path, PurePosixPath):
    # ...

# New code
if isinstance(path, Traversable):
    # ...
```

If you rely on `PurePosixPath`-specific methods not available on `Traversable`:

```python
# If you need PurePosixPath for path operations, convert explicitly
from pathlib import PurePosixPath
traversable = make_path(Heading, "static/styles.css")
pure_path = PurePosixPath(str(traversable))
```

**Benefits of Traversable:**

- **Package-Oriented:** Natural support for `package:path` syntax
- **Resource Access:** Direct file operations with `.is_file()`, `.read_text()`, etc.
- **Type Alignment:** Better represents resources from packages vs filesystem paths
- **Extensibility:** Supports custom resource loaders beyond filesystem

## Development Status

**Current Phase:** Phase 4 - Traversable and Package Paths (Complete)

### Phase 1 - Core Path API (Complete)

- ✅ `make_path()` function for component asset resolution
- ✅ Converts Python module names to web paths
- ✅ Returns `Traversable` for resource access
- ✅ Handles repeated module names (e.g., `heading.heading` → `heading`)
- ✅ Works with classes, instances, and any object with `__module__`
- ✅ Type safe with comprehensive type hints
- ✅ 15 focused tests covering core functionality
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
- ✅ Comprehensive tests
- ✅ Type safe with ty compliance

### Phase 3 - Path Rendering (Complete)

- ✅ `render_path_nodes()` function for final HTML rendering
- ✅ `RenderStrategy` Protocol for extensible rendering strategies
- ✅ `RelativePathStrategy` with optional site_prefix support
- ✅ Transforms TraversableElement to Element with string paths
- ✅ Calculates relative paths from target to source
- ✅ Processes any Traversable attribute (not just href/src)
- ✅ Tree walking helper `_walk_tree()` for reusable traversal
- ✅ Immutable transformations with optimization
- ✅ Type safe with ty compliance

### Phase 4 - Traversable and Package Paths (Complete)

- ✅ Package asset support with `package:path` syntax
- ✅ Colon-based automatic path type detection
- ✅ `Traversable` as primary return type
- ✅ Support for relative paths (plain, `./`, `../`)
- ✅ Package path parsing and resolution
- ✅ Asset existence validation with fail-fast errors
- ✅ Test fixtures for package resources
- ✅ 27 tests covering package and relative path workflows
- ✅ Integration tests for end-to-end pipelines
- ✅ Type safe with Traversable support

### Design Decisions

- **Simple API:** Direct functions instead of class-based API
- **Traversable-First:** Resource-oriented paths for package and file assets
- **Package-Centric:** First-class `package:path` syntax support
- **Component-centric:** Pass component objects directly, framework extracts `__module__`
- **Immutable Transformations:** Tree rewriting creates new nodes, doesn't mutate originals
- **Decorator Pattern:** Optional decorator for convenience, function always available for explicit use
- **Fail-Fast Validation:** Immediate error reporting with clear context
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
2. **Resource-Oriented:** Traversable paths for both package and file resources
3. **Package-First:** Native support for `package:path` syntax
4. **Cross-Platform:** Traversable ensures consistent resource access
5. **Web-First Design:** Paths designed for HTML rendering and resource access
6. **Component-centric:** Pass component objects directly, framework extracts `__module__`
7. **Type Safety First:** Comprehensive type hints enable excellent IDE support
8. **Immutable by Default:** Tree transformations create new structures
9. **Fail-Fast Validation:** Clear errors when assets don't exist
10. **Keep It Simple:** No complex policies or abstractions - direct resource resolution

## License

[Add license information]

## Contributing

[Add contribution guidelines]

## Performance

### Overview

`tdom-path` is highly optimized for real-world usage, particularly Static Site Generation (SSG) workflows where components are reused across multiple pages. The library uses LRU caching for module loading, providing **17.9x speedup** for cached accesses.

### Quick Benchmark

```bash
# Run standalone performance benchmark
just benchmark

# Run pytest-based performance tests
just test -m slow
```

### Real-World Performance Results

Based on benchmarks simulating typical SSG workflows (120+ component tree, multiple pages):

| Operation | Cold Cache | Warm Cache | Speedup |
|-----------|------------|------------|---------|
| `make_path()` - module access | 25.8μs | 1.4μs | **17.9x faster** |
| `make_path()` - package path | ~25μs | 1.3μs | **19x faster** |
| `make_path_nodes()` - tree transform | 758μs | 758μs | (no change) |
| `render_path_nodes()` - per page | 684μs | 684μs | (no change) |

**Cache Impact:** **1688% faster (17.9x)** with warm cache ✓ EXCELLENT

### Why This Matters

**SSG Scenario:** Building 100 pages with the same component:
- **Without cache:** 100 × 25μs = 2,500μs = 2.5ms
- **With cache:** 1 × 25μs + 99 × 1.4μs = 164μs = 0.16ms
- **Savings:** **94% faster** (2.34ms saved)

For sites with 1000+ pages, the savings are even more dramatic.

### Performance Characteristics

**Excellent:**
- Path resolution (cached): 1.4μs ✓ EXCELLENT
- Module loading optimization: 17.9x speedup ✓ EXCELLENT

**Good:**
- Tree traversal: ~450μs for 120+ components ✓ GOOD
- Multi-page rendering: 684μs/page ✓ GOOD

### How the Cache Works

The library uses `@lru_cache(maxsize=128)` for module loading via `importlib.resources.files()`:

```python
@lru_cache(maxsize=128)
def _get_module_files(module_name: str) -> Traversable:
    """Cache Traversable roots to avoid repeated module loading."""
    return files(module_name)
```

**First access (cold cache):**
- Loads module metadata: ~20μs
- Sets up resource reader: ~5μs
- **Total: ~25μs**

**Subsequent accesses (warm cache):**
- Dictionary lookup: ~1.4μs
- **Total: ~1.4μs**

**Cache benefits:**
- Zero overhead on first use
- Massive speedup on repeated use
- Automatic cleanup (LRU eviction)
- Thread-safe (Python's LRU cache is lock-based)

### Profiling Tools

The library includes standalone profiling tools for performance analysis:

```bash
# Run comprehensive benchmark suite
just benchmark

# Profile specific operations
uv run python -m tdom_path.profiling.benchmark
```

**Benchmark features:**
- Cold vs warm cache comparison
- SSG workflow simulation (multi-page rendering)
- Clear performance analysis with thresholds
- Real-world usage patterns

### Optimization Details

**What was optimized:**
- Module loading via `importlib.resources.files()` (80% of transformation time)
- Added LRU cache for Traversable module roots
- One-line change at call sites

**What wasn't optimized (and why):**
- Tree traversal - already efficient (~2μs per node)
- Path calculations - necessary operations
- isinstance() checks - highly optimized in CPython

### Performance Testing

```bash
# Run pytest-based performance tests
just test -m slow

# Run with free-threaded Python (regression detection)
just test-freethreaded -m slow

# Run with parallel execution (8 threads, 10 iterations)
just test-freethreaded -m slow --threads=8 --iterations=10
```

**Test infrastructure:**
- pytest-benchmark for standardized timing
- tracemalloc for memory profiling
- Realistic test data (100+ component trees)
- Free-threaded Python compatibility
- Baseline metrics documented in tests

### When to Expect Peak Performance

**Best case (warm cache):**
- SSG workflows (reusing components)
- Long-running servers (modules stay loaded)
- Component libraries (shared across pages)
- Development with hot reload (cache persists)

**First-time use (cold cache):**
- Initial page build
- Fresh Python process
- New module references
- Still fast (25μs), just not cached

### Memory Usage

- **LRU cache:** ~128 entries × ~1KB = ~128KB max
- **Per operation:** Minimal overhead (~10-50KB)
- **Tree operations:** Linear with tree size (~1-5MB for 100+ components)

### Performance Tips

1. **Reuse components** - Same component across pages = cache hits
2. **Build incrementally** - Keep Python process alive between builds
3. **Use package paths** - Already optimized with cache
4. **Profile your workflow** - Use `just benchmark` to measure your patterns
5. **Monitor cache** - Check `_get_module_files.cache_info()` for hit/miss ratio

The library is designed for the common case: building multiple pages with shared components. The LRU cache ensures this workflow is extremely fast.

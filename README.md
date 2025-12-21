# tdom-path

Component resource path utilities for web applications using module-relative paths

## Overview

`tdom-path` provides utilities for resolving component static assets (CSS, JS, images) in component-based
web applications. It converts Python module names to web paths, returning `PurePosixPath` objects that
represent module-relative locations suitable for web rendering.

## Features

- **Component Asset Resolution:** Pass component classes/instances directly to resolve static assets
- **Tree Rewriting:** Automatically transform `<link>` and `<script>` elements to use PurePosixPath
- **Decorator Support:** Use `@path_nodes` decorator for automatic tree transformation
- **Module-Relative Paths:** Returns paths like `mysite/components/heading/static/styles.css`
- **Cross-Platform:** PurePosixPath ensures consistent `/` separators for web paths
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

# Get module-relative path to component's static asset
css_path = make_path(Heading, "static/styles.css")

# Returns PurePosixPath with module-relative path
print(css_path)  # mysite/components/heading/static/styles.css
print(type(css_path))  # <class 'pathlib.PurePosixPath'>

# Use in HTML rendering
html = f'<link rel="stylesheet" href="{css_path}">'
# <link rel="stylesheet" href="mysite/components/heading/static/styles.css">

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
# transformed to PurePosixPath objects using make_path()
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

# Transform tree to use PurePosixPath
new_tree = make_path_nodes(tree, Heading)
# new_tree now has PurePosixPath objects in link href and script src attributes
```

## Module-Relative Paths

`make_path` converts Python module names to web paths by replacing dots with slashes:

```python
from tdom_path import make_path
from mysite.components.heading import Heading

# Module: mysite.components.heading
# Asset: static/styles.css
# Result: mysite/components/heading/static/styles.css

css_path = make_path(Heading, "static/styles.css")
print(str(css_path))  # mysite/components/heading/static/styles.css
```

## Tree Rewriting

The tree rewriting functionality walks a tdom Node tree and automatically detects elements with static asset references (`<link>` and `<script>` tags), converting their `href`/`src` attribute values from strings to PurePosixPath objects.

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
        # Local CSS - transformed to PurePosixPath
        Element("link", {
            "rel": "stylesheet",
            "href": "static/styles.css"
        }),
    ])
```

## API Reference

### make_path

```python
def make_path(component: Any, asset: str) -> PurePosixPath
```

Create path to component asset using module-relative paths.

**Parameters:**
- `component`: Python object with `__module__` attribute (class, function, instance, etc.)
- `asset`: Relative path to the asset within the component package (e.g., `"static/styles.css"`)

**Returns:**
- `PurePosixPath` representing the module-relative path

**Raises:**
- `TypeError`: If component doesn't have `__module__` attribute

**Examples:**
```python
# Get CSS file path
css_path = make_path(Heading, "static/styles.css")
# Returns: PurePosixPath('mysite/components/heading/static/styles.css')

# Get JavaScript file path
js_path = make_path(Heading, "static/script.js")

# Get image in subdirectory
img_path = make_path(Heading, "static/images/logo.png")
```

### make_path_nodes

```python
def make_path_nodes(target: Node, component: Any) -> Node
```

Rewrite asset-bearing attributes in a tdom tree to use make_path.

Walks the Node tree and detects elements with static asset references (`<link>` and `<script>` tags), converting their `href`/`src` string attributes to PurePosixPath using `make_path(component, attr_value)`.

**Parameters:**
- `target`: Root node of the tree to process
- `component`: Component instance/class for make_path() resolution

**Returns:**
- New Node tree with asset attributes converted to PurePosixPath (immutable transformation)

**Examples:**
```python
from tdom import Element
from mysite.components.heading import Heading

# Create tree with string references
tree = Element("head", children=[
    Element("link", {"rel": "stylesheet", "href": "static/styles.css"})
])

# Transform to use PurePosixPath
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

### render_path_nodes

```python
def render_path_nodes(
    tree: Node,
    target: PurePosixPath,
    strategy: RenderStrategy | None = None
) -> Node
```

Render PathElement nodes to Element nodes with relative path strings.

Walks the Node tree, detects PathElement instances containing PurePosixPath attribute values, and transforms them into regular Element instances with those paths rendered as strings using the provided strategy.

This is the final rendering step after `make_path_nodes()` has converted asset paths to PurePosixPath instances. It calculates the appropriate string representation for each path based on the target output location.

**Parameters:**
- `tree`: Root node of the tree to process
- `target`: PurePosixPath target output location (e.g., `"mysite/pages/index.html"`)
- `strategy`: Optional RenderStrategy for path calculation. Defaults to `RelativePathStrategy()` if None.

**Returns:**
- New Node tree with PathElement nodes transformed to Element nodes containing string path attributes

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
        <link rel="stylesheet" href="static/styles.css">
    </head>
''')

# Step 2: Transform to PathElement with PurePosixPath
path_tree = make_path_nodes(tree, Heading)

# Step 3: Render to Element with relative path strings
target = PurePosixPath("mysite/pages/about.html")
rendered = render_path_nodes(path_tree, target)
# Link now has href="../../components/heading/static/styles.css"

# With site prefix for subdirectory deployment
strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
rendered = render_path_nodes(path_tree, target, strategy=strategy)
# Link now has href="mysite/static/mysite/components/heading/static/styles.css"
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
# Returns: "../../components/heading/static/styles.css"

# With site prefix for subdirectory deployment
strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
path_str = strategy.calculate_path(source, target)
# Returns: "mysite/static/mysite/components/heading/static/styles.css"
```

### RenderStrategy Protocol

```python
class RenderStrategy(Protocol):
    def calculate_path(self, source: PurePosixPath, target: PurePosixPath) -> str:
        ...
```

Protocol for path rendering strategies.

Defines the interface for calculating how PurePosixPath paths should be rendered as strings in the final HTML output. Implementations can provide different rendering strategies such as relative paths, absolute paths, CDN URLs, etc.

**Extensibility:**
Create custom strategies by implementing the protocol:

```python
from pathlib import PurePosixPath
from tdom_path.tree import RenderStrategy

class AbsolutePathStrategy:
    """Render all paths as absolute URLs."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def calculate_path(self, source: PurePosixPath, target: PurePosixPath) -> str:
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

# 1. Define your component with string asset paths
class Heading:
    def __html__(self):
        return html(t'''
            <div class="heading">
                <link rel="stylesheet" href="static/heading.css">
                <script src="static/heading.js"></script>
                <h1>Welcome</h1>
            </div>
        ''')

# 2. Transform string paths to PurePosixPath (component-relative)
heading = Heading()
tree = heading.__html__()
path_tree = make_path_nodes(tree, heading)
# Link href is now: PurePosixPath('mysite/components/heading/static/heading.css')
# Script src is now: PurePosixPath('mysite/components/heading/static/heading.js')

# 3. Render for a specific target page (relative paths)
target = PurePosixPath("mysite/pages/about.html")
rendered_tree = render_path_nodes(path_tree, target)
# Link href is now: "../../components/heading/static/heading.css"
# Script src is now: "../../components/heading/static/heading.js"

# 4. Convert to HTML string
html_output = str(rendered_tree)
# <div class="heading">
#   <link rel="stylesheet" href="../../components/heading/static/heading.css" />
#   <script src="../../components/heading/static/heading.js"></script>
#   <h1>Welcome</h1>
# </div>
```

## Development Status

**Current Phase:** Phase 3 - Path Rendering (Complete)

### Phase 1 - Core Path API (Complete)

- ✅ `make_path()` function for component asset resolution
- ✅ Converts Python module names to web paths
- ✅ Returns `PurePosixPath` for module-relative paths
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

### Phase 3 - Path Rendering (Complete)

- ✅ `render_path_nodes()` function for final HTML rendering
- ✅ `RenderStrategy` Protocol for extensible rendering strategies
- ✅ `RelativePathStrategy` with optional site_prefix support
- ✅ Transforms PathElement to Element with string paths
- ✅ Calculates relative paths from target to source
- ✅ Processes any PurePosixPath attribute (not just href/src)
- ✅ Tree walking helper `_walk_tree()` for reusable traversal
- ✅ Immutable transformations with optimization (same object when unchanged)
- ✅ 18 focused tests including 6 integration tests
- ✅ Type safe with ty compliance

### Design Decisions

- **Simple API:** Direct functions instead of class-based API
- **Module-Relative Paths:** Returns `PurePosixPath` for web-ready module paths
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
2. **Module-Relative Paths:** Convert Python modules to web paths automatically
3. **Cross-Platform:** PurePosixPath ensures consistent `/` separators for web
4. **Web-First Design:** Paths designed for HTML rendering, not filesystem operations
5. **Component-centric:** Pass component objects directly, framework extracts `__module__`
6. **Type Safety First:** Comprehensive type hints enable excellent IDE support
7. **Immutable by Default:** Tree transformations create new structures
8. **Keep It Simple:** No complex policies or abstractions - direct path resolution only

## License

[Add license information]

## Contributing

[Add contribution guidelines]

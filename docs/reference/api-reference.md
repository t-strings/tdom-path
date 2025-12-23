# API Reference

This section provides detailed API documentation for tdom-path.

## Core Functions

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
   - Resolved relative to the component's module
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

## Decorators

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

## Rendering Functions

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

## Strategy Classes

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

## Auto-generated API Documentation

For complete API documentation generated from docstrings, please build the documentation:

```bash
just docs
```

The auto-generated API docs will include all functions, classes, and methods with their parameters, return types, and examples.

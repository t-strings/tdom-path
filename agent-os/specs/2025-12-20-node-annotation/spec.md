# Specification: make_path_nodes - Tree Rewriting for Component Assets

## Goal

Create a `make_path_nodes()` function that walks a tdom Node tree, detects elements with static asset references (
`<link>` and `<script>` tags), and converts their `href`/`src` attribute values from strings to `PurePosixPath` objects
using `make_path()`. Provide both a function and decorator version for easy component integration.

## User Stories

- As a component author, I want to write `<link href="static/styles.css">` and have it automatically converted to use
  `make_path()`
- As a developer, I want a tree rewriting function that finds all asset references and resolves them using
  importlib.resources
- As a framework user, I want a decorator I can apply to my component's `__html__()` method to automatically process
  asset paths
- As a component library maintainer, I want the tree walking logic to match proven patterns from tdom-sphinx

## Specific Requirements

**make_path_nodes Function**

- Function signature: `make_path_nodes(target: Node, component: Any) -> Node`
- Walk the entire Node tree recursively
- Detect `<link>` tags with `href` attribute (anywhere in tree)
- Detect `<script>` tags with `src` attribute (anywhere in tree)
- For each detected element:
    - Extract the attribute value (href or src)
    - Call `make_path(component, attr_value)` to get PurePosixPath
    - Create new Element with PurePosixPath as attribute value
    - Preserve all other attributes unchanged
- Return a new Node tree with updated elements (immutable transformation)
- Skip external URLs (http://, https://, //, etc.)
- Skip special schemes (mailto:, tel:, data:, javascript:)
- Skip anchor-only links (#...)

**path_nodes Decorator**

- Decorator signature: `@path_nodes` (no arguments needed)
- Supports both function components and class components
- For function components: extracts component from function itself
- For class components: extracts component from `self` parameter in `__call__()` or `__html__()`
- Wraps the decorated function/method to process returned Node tree
- Usage: Add `@path_nodes` above function component or class method
- Only works with functions/methods that return Node (not str)
- Returns transformed Node with PurePosixPath attributes

**Tree Walking Logic**

- Use recursive walking pattern from tdom-sphinx's `relative_tree()`
- Process `<link>` tags anywhere in tree
- Process `<script>` tags anywhere in tree
- Use `getattr(node, "tag", None)` for safe attribute access
- Use `getattr(node, "attrs", None)` for safe dict access
- Use `getattr(node, "children", None)` for safe children access
- Recursively walk all children

**Element Detection Rules**

- `<link>` tags: Process `href` attribute anywhere in tree
- `<script>` tags: Process `src` attribute anywhere in tree
- Skip external URLs: `http://`, `https://`, `//`
- Skip special schemes: `mailto:`, `tel:`, `data:`, `javascript:`
- Skip anchor-only: `#...`
- Process only relative paths starting with `./` or direct filenames

**Immutable Tree Transformation**

- Create new Element instances (don't mutate original)
- Preserve children by copying
- Preserve all attributes except the one being transformed
- Return new tree structure with updated elements
- Original tree remains unchanged

**Type Safety**

- Import `Node`, `Element` from tdom
- Import `PurePosixPath` from importlib.resources.abc
- Type hint for component: `Any` (matches make_path)
- Return type: `Node`
- Works with ty type checker

## Design Decisions

**Function vs Decorator**

- Provide both: `make_path_nodes()` function for explicit use, `@path_nodes` decorator for convenience
- Decorator extracts component automatically from `self`
- Both use same underlying tree walking logic

**Tree Walking Pattern**

- Follow tdom-sphinx's proven `relative_tree()` pattern
- Track context (in_head, in_body) during traversal
- Safe attribute access with getattr and defaults
- Recursive walking through children

**Immutability**

- Don't mutate original tree (create new elements)
- Safer for debugging and reasoning
- Aligns with functional programming principles
- Future-proof for frozen dataclasses

**Element Detection Strategy**

- Match tdom-sphinx's logic for consistency
- `<link>` anywhere in tree (stylesheets, preload, etc.)
- `<script>` anywhere in tree (scripts can be in head or body)
- Skip external/special URLs (no point resolving those)

**Attribute Preservation**

- Only transform the href/src attribute
- Keep all other attributes unchanged (rel, type, class, etc.)
- Maintain attribute order where possible

## Implementation

**File: `src/tdom_path/tree.py`** (new file)

```python
"""Tree rewriting utilities for component asset path resolution."""

from typing import Any

from importlib.resources.abc import PurePosixPath
from tdom import Element, Node

from tdom_path.webpath import make_path


def _should_process_href(href: str) -> bool:
    """Check if href should be processed (skip external/special URLs)."""
    if not isinstance(href, str) or not href:
        return False

    lower = href.lower()
    if (
        lower.startswith("http://")
        or lower.startswith("https://")
        or lower.startswith("//")
        or lower.startswith("mailto:")
        or lower.startswith("tel:")
        or lower.startswith("data:")
        or lower.startswith("javascript:")
        or href.startswith("#")
    ):
        return False

    return True


def _transform_link_element(element: Element, component: Any) -> Element:
    """Transform <link> element's href to PurePosixPath."""
    attrs = element.attrs.copy()
    href = attrs.get("href")

    if _should_process_href(href):
        # Convert href to PurePosixPath using make_path
        attrs["href"] = make_path(component, href)

    return Element(
        tag=element.tag,
        attrs=attrs,
        children=element.children.copy() if element.children else [],
    )


def _transform_script_element(element: Element, component: Any) -> Element:
    """Transform <script> element's src to PurePosixPath."""
    attrs = element.attrs.copy()
    src = attrs.get("src")

    if _should_process_href(src):
        # Convert src to PurePosixPath using make_path
        attrs["src"] = make_path(component, src)

    return Element(
        tag=element.tag,
        attrs=attrs,
        children=element.children.copy() if element.children else [],
    )


def make_path_nodes(target: Node, component: Any) -> Node:
    """Rewrite asset-bearing attributes in a tdom tree to use make_path.

    Walks the Node tree and detects elements with static asset references:
    - <link> tags in <head> with href attributes
    - <script> tags with src attributes

    For each detected element, converts the href/src string attribute to a
    PurePosixPath using make_path(component, attr_value).

    External URLs (http://, https://, //), special schemes (mailto:, tel:,
    data:, javascript:), and anchor-only links (#...) are left unchanged.

    Args:
        target: Root node of the tree to process
        component: Component instance/class for make_path() resolution

    Returns:
        New Node tree with asset attributes converted to PurePosixPath

    Examples:
        >>> from tdom import Element, Text
        >>> from mysite.components.heading import Heading
        >>>
        >>> # Original tree with string href
        >>> link = Element("link", {"rel": "stylesheet", "href": "static/styles.css"})
        >>> tree = Element("head", children=[link])
        >>>
        >>> # Transform to use PurePosixPath
        >>> new_tree = make_path_nodes(tree, Heading)
        >>> # new_tree now has PurePosixPath in link's href
    """

    def walk(node: Node) -> Node:
        """Recursively walk tree and transform asset-bearing elements."""
        tag = getattr(node, "tag", None)
        attrs = getattr(node, "attrs", None)
        children = getattr(node, "children", None)

        # Transform <link> tags anywhere
        if tag == "link" and isinstance(attrs, dict):
            return _transform_link_element(node, component)

        # Transform <script> tags anywhere
        if tag == "script" and isinstance(attrs, dict):
            return _transform_script_element(node, component)

        # Recursively process children
        if isinstance(children, (list, tuple)) and children:
            new_children = [walk(child) for child in children]
            # Return new Element with transformed children
            if hasattr(node, "tag"):
                return Element(
                    tag=tag,
                    attrs=attrs.copy() if isinstance(attrs, dict) else {},
                    children=new_children,
                )
            # For Fragment or other node types, return as-is
            # (this is simplified; real implementation may need to handle Fragment)
            return node

        # Leaf node or no children, return as-is
        return node

    return walk(target)


def path_nodes(func_or_method):
    """Decorator to automatically apply make_path_nodes to component output.

    Supports both function components and class component methods.
    For function components, uses the function itself as the component.
    For class methods (__call__ or __html__), uses self as the component.

    Usage:
        # Function component
        @path_nodes
        def heading(text: str) -> Element:
            return Element("link", {"href": "static/styles.css"})

        # Class component with __call__
        class Heading:
            @path_nodes
            def __call__(self) -> Element:
                return Element("link", {"href": "static/styles.css"})

        # Class component with __html__
        class Heading:
            @path_nodes
            def __html__(self) -> Element:
                return Element("link", {"href": "static/styles.css"})

    Args:
        func_or_method: The function or method to wrap

    Returns:
        Wrapped callable that applies make_path_nodes
    """
    import inspect

    def wrapper(*args, **kwargs):
        # Call original function/method to get Node
        result = func_or_method(*args, **kwargs)

        # Determine component: function itself or self from method
        if inspect.ismethod(func_or_method) or (args and hasattr(args[0], '__dict__')):
            # Method call - use self (first arg) as component
            component = args[0]
        else:
            # Function call - use function itself as component
            component = func_or_method

        # Apply transformation and return
        return make_path_nodes(result, component)

    return wrapper
```

**File: `src/tdom_path/__init__.py`** (update)

```python
"""tdom-path: Component resource path utilities for web applications.

Phase 1: Core Path API - make_path with importlib.resources integration
Phase 2: Tree Rewriting - make_path_nodes for automatic asset resolution
"""

from tdom_path.tree import make_path_nodes, path_nodes
from tdom_path.webpath import make_path

__all__ = ["make_path", "make_path_nodes", "path_nodes"]
```

## Example Usage

**Using make_path_nodes Function Directly**

```python
from tdom import Element, Text
from tdom_path import make_path_nodes


class Heading:
    def __html__(self) -> Element:
        # Create tree with string asset references
        link = Element("link", {"rel": "stylesheet", "href": "static/styles.css"})
        script = Element("script", {"src": "static/script.js"})
        h1 = Element("h1", children=[Text(self.text)])
        head = Element("head", children=[link, script])
        body = Element("body", children=[h1])
        html = Element("html", children=[head, body])

        # Transform tree to use PurePosixPath
        return make_path_nodes(html, self)
```

**Using @path_nodes Decorator**

```python
from tdom import Element, Text
from tdom_path import path_nodes


class Heading:
    @path_nodes
    def __html__(self) -> Element:
        # Just write string paths, decorator handles transformation
        link = Element("link", {"rel": "stylesheet", "href": "static/styles.css"})
        script = Element("script", {"src": "static/script.js"})
        h1 = Element("h1", children=[Text(self.text)])
        head = Element("head", children=[link, script])
        body = Element("body", children=[h1])
        return Element("html", children=[head, body])
```

**Mixed External and Local Assets**

```python
from tdom_path import path_nodes


class Page:
    @path_nodes
    def __html__(self):
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

## Out of Scope

**Not Included in This Phase:**

- Converting PurePosixPath back to strings for final HTML output (that's later phases)
- Relative path calculation
- Path rewriting strategies
- Context-based resolution
- `<img>` tag processing (focus on link/script first)
- `<a href>` link processing (focus on assets first)
- Build-time validation
- Asset collection for SSG

**Future Phases Will Add:**

- Phase 3: Convert PurePosixPath to strings during final rendering
- Phase 4: Relative path calculation based on render target
- Phase 5: Process `<img>` and `<a>` tags
- Phase 6: Context-based resolution strategies

## Testing Requirements

**Test File: `tests/test_tree.py`** (new file)

1. **test_make_path_nodes_link_in_head** - Transform <link> tag in <head>
2. **test_make_path_nodes_script_tag** - Transform <script> tag with src
3. **test_make_path_nodes_external_urls** - Skip http://, https://, //
4. **test_make_path_nodes_special_schemes** - Skip mailto:, tel:, data:, javascript:
5. **test_make_path_nodes_anchor_only** - Skip #... links
6. **test_make_path_nodes_mixed_assets** - Both local and external in same tree
7. **test_make_path_nodes_nested_children** - Deep tree traversal works
8. **test_make_path_nodes_preserves_other_attrs** - rel, type, class unchanged
9. **test_make_path_nodes_link_in_body** - <link> in body transformed (links processed anywhere)
10. **test_path_nodes_decorator_class_component** - Decorator on class __call__ method works
11. **test_path_nodes_decorator_function_component** - Decorator on function component works
12. **test_make_path_nodes_real_component** - Full integration with Heading component

## Acceptance Criteria

- ✓ make_path_nodes() function implemented
- ✓ @path_nodes decorator implemented
- ✓ Decorator supports both function and class components
- ✓ Tree walking follows tdom-sphinx pattern
- ✓ Detects <link> anywhere in tree (not just in head)
- ✓ Detects <script> anywhere in tree
- ✓ Converts href/src to PurePosixPath using make_path()
- ✓ Skips external URLs and special schemes
- ✓ Immutable transformation (creates new tree)
- ✓ All 12 tests pass
- ✓ 100% test coverage
- ✓ Type checking passes (ty)
- ✓ Documentation complete

## Integration Points

**Phase 1 (make_path):**

- make_path_nodes calls make_path() to get PurePosixPath
- Seamless integration: tree walking → make_path → PurePosixPath

**Future Phase 3 (Element Rendering):**

- Override Element.__str__() to convert PurePosixPath to strings
- Or provide custom rendering function
- make_path_nodes creates tree with PurePosixPath, Phase 3 renders it

**Future Phase 4 (Relative Paths):**

- Add target parameter to make_path_nodes
- Calculate relative paths during transformation
- Context-aware resolution

"""Tree rewriting utilities for component asset path resolution."""

import inspect
import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
# Use PurePosixPath instead of PurePath to ensure cross-platform consistency
# Web paths must always use forward slashes (/), never backslashes (\)
# PurePosixPath guarantees POSIX-style paths regardless of OS
from pathlib import PurePosixPath
from typing import Any, ParamSpec, Protocol, TypeGuard

from tdom import Element, Fragment, Node
from tdom_path.webpath import make_path

# Type variables for decorator
P = ParamSpec("P")
type R = Node

# Compile regex once at module load time for performance
_EXTERNAL_URL_PATTERN = re.compile(
    r"^(https?://|//|mailto:|tel:|data:|javascript:|#)", re.IGNORECASE
)


@dataclass(slots=True)
class PathElement(Element):
    """Element subclass that allows PurePosixPath attribute values.

    This class extends Element to support PurePosixPath instances in attribute
    values, enabling the tree walker to preserve type information for component
    asset paths through the rendering pipeline.

    The attrs field accepts str, PurePosixPath, or None values. During rendering,
    PurePosixPath values are automatically converted to strings via __str__(),
    producing module-relative path strings in the final HTML output.

    All other behavior is inherited from Element, including __post_init__
    validation and __str__() rendering.

    Examples:
        >>> from pathlib import PurePosixPath
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>>
        >>> # Create element with PurePosixPath href
        >>> path = make_path(Heading, "static/styles.css")
        >>> elem = PathElement(
        ...     tag="link",
        ...     attrs={"rel": "stylesheet", "href": path},
        ...     children=[]
        ... )
        >>>
        >>> # Renders to HTML with path auto-converted
        >>> str(elem)
        '<link rel="stylesheet" href="mysite/components/heading/static/styles.css" />'
    """

    attrs: dict[str, str | PurePosixPath | None]


def _should_process_href(href: str | None) -> TypeGuard[str]:
    """Check if href should be processed (skip external/special URLs).

    Args:
        href: The href or src attribute value to check

    Returns:
        True if the href should be processed (narrows type to str), False otherwise
    """
    if not isinstance(href, str) or not href:
        return False

    return not _EXTERNAL_URL_PATTERN.match(href)


def _walk_tree(node: Node, transform_fn: Callable[[Node], Node]) -> Node:
    """Recursively walk a Node tree and apply a transformation function.

    This helper function provides a generic tree-walking mechanism that:
    - Recursively traverses Element and Fragment nodes with children
    - Applies the transform_fn to each node in the tree
    - Maintains immutability by creating new nodes only when changes occur
    - Optimizes by returning the same object reference when no transformations applied

    The transform_fn is called on every node before recursing into children,
    allowing it to transform the node itself. The function should return the
    node unchanged if no transformation is needed, or return a new node instance
    if a transformation is applied.

    Args:
        node: Root node of the tree to walk
        transform_fn: Function that takes a Node and returns a Node (transformed or same)

    Returns:
        New Node tree with transformations applied, or the same object if unchanged

    Examples:
        >>> from tdom import Element, Text
        >>>
        >>> # Add a data attribute to all Elements
        >>> def add_data_attr(node):
        ...     if isinstance(node, Element):
        ...         new_attrs = {**node.attrs, "data-visited": "true"}
        ...         return Element(tag=node.tag, attrs=new_attrs, children=node.children)
        ...     return node
        >>>
        >>> tree = Element(tag="div", attrs={}, children=[Text("Hello")])
        >>> result = _walk_tree(tree, add_data_attr)
        >>> result.attrs["data-visited"]
        'true'
    """
    # Apply transformation to current node first
    transformed = transform_fn(node)

    # Recurse into children if node has them
    match transformed:
        # Element with children - recurse and rebuild if any child changed
        case Element(children=children) if children:
            new_children = [_walk_tree(child, transform_fn) for child in children]
            # Optimization: Only create new Element if children actually changed
            # This uses identity checks (is) rather than equality (==) for performance
            # If no children changed, return the original transformed node to save memory
            if any(new is not old for new, old in zip(new_children, children)):
                return Element(
                    tag=transformed.tag,
                    attrs=transformed.attrs.copy() if transformed.attrs else {},
                    children=new_children,
                )
            # Return same object if unchanged - allows callers to detect no-ops with `is`
            return transformed

        # Fragment with children - recurse and rebuild if any child changed
        case Fragment(children=children) if children:
            new_children = [_walk_tree(child, transform_fn) for child in children]
            # Optimization: Only create new Fragment if children actually changed
            if any(new is not old for new, old in zip(new_children, children)):
                return Fragment(children=new_children)
            # Return same object if unchanged - allows callers to detect no-ops with `is`
            return transformed

        # All other nodes (Text, Comment, leaf elements, etc.)
        case _:
            return transformed


def _transform_asset_element(
    element: Element, attr_name: str, component: Any
) -> Element | PathElement:
    """Transform element's asset attribute to PurePosixPath.

    Args:
        element: The element to transform (link or script)
        attr_name: The attribute name to transform ("href" or "src")
        component: Component instance/class for make_path() resolution

    Returns:
        New Element or PathElement with asset attribute transformed to PurePosixPath
    """
    attr_value = element.attrs.get(attr_name)

    # Only transform if it's a processable local path
    if not _should_process_href(attr_value):
        return element

    # TypeGuard ensures attr_value is str, but add assert for type checker
    assert isinstance(attr_value, str)

    # Create dict that accepts Any values (including PurePosixPath)
    attrs = dict[str, Any](element.attrs)
    attrs[attr_name] = make_path(component, attr_value)

    # Check if any attr value is PurePosixPath - if so, use PathElement
    has_path = any(isinstance(v, PurePosixPath) for v in attrs.values())

    if has_path:
        return PathElement(
            tag=element.tag,
            attrs=attrs,
            children=element.children,
        )
    else:
        return Element(
            tag=element.tag,
            attrs=attrs,
            children=element.children,
        )


def make_path_nodes(target: Node, component: Any) -> Node:
    """Rewrite asset-bearing attributes in a tdom tree to use make_path.

    Walks the Node tree and detects elements with static asset references:
    - <link> tags with href attributes (anywhere in tree)
    - <script> tags with src attributes (anywhere in tree)

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
        >>> from tdom import html
        >>> from mysite.components.heading import Heading
        >>>
        >>> # Original tree with string href
        >>> tree = html(t'''
        ...     <head>
        ...         <link rel="stylesheet" href="static/styles.css">
        ...     </head>
        ... ''')
        >>>
        >>> # Transform to use PurePosixPath
        >>> new_tree = make_path_nodes(tree, Heading)
        >>> # new_tree now has PurePosixPath in link's href
    """

    def transform(node: Node) -> Node:
        """Transform asset-bearing elements to use PurePosixPath."""
        match node:
            # Transform <link> elements with href
            case Element(tag="link"):
                return _transform_asset_element(node, "href", component)

            # Transform <script> elements with src
            case Element(tag="script"):
                return _transform_asset_element(node, "src", component)

            # All other nodes - return unchanged
            case _:
                return node

    return _walk_tree(target, transform)


class RenderStrategy(Protocol):
    """Protocol for path rendering strategies.

    Defines the interface for calculating how PurePosixPath paths should be
    rendered as strings in the final HTML output. Implementations can provide
    different rendering strategies such as relative paths, absolute paths,
    CDN URLs, etc.

    The protocol requires a single method that takes a source PurePosixPath
    and target output location, returning the string representation to use
    in the rendered HTML.

    Examples:
        >>> from pathlib import PurePosixPath
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>>
        >>> # Use default relative path strategy
        >>> strategy = RelativePathStrategy()
        >>> source = make_path(Heading, "static/styles.css")
        >>> target = PurePosixPath("pages/about.html")
        >>> path_str = strategy.calculate_path(source, target)
        >>> # Returns relative path from pages/about.html to static/styles.css
        >>>
        >>> # Custom strategy with site prefix
        >>> prefixed_strategy = RelativePathStrategy(site_prefix="mysite/static")
        >>> path_str = prefixed_strategy.calculate_path(source, target)
        >>> # Returns path prefixed with "mysite/static"
    """

    def calculate_path(self, source: PurePosixPath, target: PurePosixPath) -> str:
        """Calculate string representation for a path in rendered output.

        Args:
            source: The PurePosixPath source path to render
            target: The PurePosixPath target output location

        Returns:
            String representation of the path for use in HTML attributes
        """
        ...


@dataclass(frozen=True, slots=True)
class RelativePathStrategy:
    """Strategy for rendering paths as relative URLs.

    Calculates relative paths from the target output location to the source
    asset location, optionally prepending a site prefix for deployment scenarios
    where assets are served from a subdirectory.

    The strategy works with PurePosixPath objects and calculates relative
    paths based on web directory structure.

    Uses PurePosixPath for all path calculations to ensure cross-platform
    consistency in web path generation.

    Args:
        site_prefix: Optional PurePosixPath prefix to prepend to all calculated paths
                    (e.g., PurePosixPath("mysite/static") for subdirectory deployments)

    Examples:
        >>> from pathlib import PurePosixPath
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>>
        >>> # Basic relative path calculation
        >>> strategy = RelativePathStrategy()
        >>> source = make_path(Heading, "static/styles.css")
        >>> target = PurePosixPath("index.html")
        >>> strategy.calculate_path(source, target)
        'static/styles.css'
        >>>
        >>> # With site prefix for subdirectory deployment
        >>> strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
        >>> strategy.calculate_path(source, target)
        'mysite/static/static/styles.css'
        >>>
        >>> # Cross-directory navigation
        >>> target = PurePosixPath("pages/about.html")
        >>> strategy.calculate_path(source, target)
        '../static/styles.css'
    """

    site_prefix: PurePosixPath | None = None

    def calculate_path(self, source: PurePosixPath, target: PurePosixPath) -> str:
        """Calculate relative path from target to source.

        Both source and target are module-relative PurePosixPath objects.
        This method calculates the relative path from the target's location
        to the source, optionally prepending a site prefix.

        Args:
            source: The PurePosixPath source asset path (module-relative)
            target: The PurePosixPath target output location (module-relative)

        Returns:
            Relative path string from target to source, with optional prefix

        Examples:
            >>> # Same directory
            >>> source = PurePosixPath("mysite/components/heading/styles.css")
            >>> target = PurePosixPath("mysite/components/heading/index.html")
            >>> strategy.calculate_path(source, target)
            'styles.css'
            >>>
            >>> # Parent directory navigation
            >>> source = PurePosixPath("mysite/components/heading/static/styles.css")
            >>> target = PurePosixPath("mysite/pages/about.html")
            >>> strategy.calculate_path(source, target)
            '../../components/heading/static/styles.css'
        """
        # If site_prefix is provided, prepend it to the source path
        # This is useful for deploying to subdirectories (e.g., GitHub Pages /repo/)
        if self.site_prefix:
            return str(self.site_prefix / source)

        # Calculate relative path from target's parent directory to source
        # Why target.parent? Because target is a file (e.g., pages/about.html),
        # and we need the directory it's in (pages/) to calculate the relative path
        target_dir = target.parent

        # Use pathlib's relative_to with walk_up=True for proper relative path calculation
        # walk_up=True allows climbing up directories with ../ notation
        # Example: from pages/about.html to components/heading/static/styles.css
        # becomes: ../components/heading/static/styles.css
        try:
            relative_path = source.relative_to(target_dir, walk_up=True)
            return str(relative_path)
        except ValueError:
            # If relative_to fails (rare edge case), return source path as-is
            return str(source)


def _render_transform_node(
    node: Node, target: PurePosixPath, strategy: RenderStrategy
) -> Node:
    """Transform PathElement nodes to Element nodes with string paths.

    Helper function that processes a single node, converting PathElement
    instances with PurePosixPath attributes into regular Element instances
    with those paths rendered as strings.

    Args:
        node: The node to transform
        target: Target output location for relative path calculation
        strategy: RenderStrategy for path calculation

    Returns:
        Transformed Element node, or original node if no transformation needed
    """
    # Only process PathElement instances
    if not isinstance(node, PathElement):
        return node

    # Check if any attribute contains a PurePosixPath
    has_path_attr = any(
        isinstance(value, PurePosixPath) for value in node.attrs.values()
    )

    # If no PurePosixPath attributes, return unchanged
    if not has_path_attr:
        return node

    # Transform PurePosixPath attributes to strings using strategy
    new_attrs: dict[str, str | None] = {}
    for attr_name, attr_value in node.attrs.items():
        if isinstance(attr_value, PurePosixPath):
            # Calculate string path using strategy
            new_attrs[attr_name] = strategy.calculate_path(attr_value, target)
        else:
            # Preserve non-PurePosixPath attributes as-is
            new_attrs[attr_name] = attr_value  # type: ignore

    # Return new Element (NOT PathElement) with string attributes
    return Element(
        tag=node.tag,
        attrs=new_attrs,
        children=node.children,
    )


def render_path_nodes(
    tree: Node, target: PurePosixPath, strategy: RenderStrategy | None = None
) -> Node:
    """Render PathElement nodes to Element nodes with relative path strings.

    Walks the Node tree, detects PathElement instances containing PurePosixPath
    attribute values, and transforms them into regular Element instances with
    those paths rendered as strings using the provided strategy.

    This function is the final rendering step after make_path_nodes() has
    converted asset paths to PurePosixPath instances. It calculates the
    appropriate string representation for each path based on the target
    output location.

    The function processes ANY attribute containing a PurePosixPath value,
    not just href and src. This enables flexible asset path handling for
    custom attributes.

    Maintains immutability by creating new nodes only when transformations
    occur. Returns the same object reference when no PathElement nodes are
    found (optimization).

    Args:
        tree: Root node of the tree to process
        target: PurePosixPath target output location (e.g., "mysite/pages/index.html")
        strategy: Optional RenderStrategy for path calculation.
                 Defaults to RelativePathStrategy() if None.

    Returns:
        New Node tree with PathElement nodes transformed to Element nodes
        containing string path attributes, or the same object if no changes needed

    Examples:
        >>> from pathlib import PurePosixPath
        >>> from tdom import html
        >>> from tdom_path import make_path_nodes, render_path_nodes
        >>> from tdom_path.tree import RelativePathStrategy
        >>> from mysite.components.heading import Heading
        >>>
        >>> # Step 1: Create tree with PathElement nodes
        >>> tree = html(t'''
        ...     <head>
        ...         <link rel="stylesheet" href="static/styles.css">
        ...     </head>
        ... ''')
        >>> path_tree = make_path_nodes(tree, Heading)
        >>>
        >>> # Step 2: Render PathElement nodes to Element with relative paths
        >>> target = PurePosixPath("mysite/pages/about.html")
        >>> rendered = render_path_nodes(path_tree, target)
        >>> # Link now has href="../../components/heading/static/styles.css"
        >>>
        >>> # With custom strategy (site prefix)
        >>> strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
        >>> rendered = render_path_nodes(path_tree, target, strategy=strategy)
        >>> # Link now has href="mysite/static/mysite/components/heading/static/styles.css"
    """
    # Default to RelativePathStrategy if no strategy provided
    if strategy is None:
        strategy = RelativePathStrategy()

    # Use _walk_tree with _render_transform_node helper
    return _walk_tree(tree, lambda node: _render_transform_node(node, target, strategy))


def path_nodes(
    func_or_method: Callable[P, R],
) -> Callable[P, R]:
    """Decorator to automatically apply make_path_nodes to component output.

    Supports both function components and class component methods.
    For function components, uses the function itself as the component.
    For class methods (__call__ or __html__), uses self as the component.

    Usage:
        # Function component
        @path_nodes
        def heading(text: str) -> Node:
            return html(t'<link rel="stylesheet" href="static/styles.css">')

        # Class component with __call__
        class Heading:
            @path_nodes
            def __call__(self) -> Node:
                return html(t'<link rel="stylesheet" href="static/styles.css">')

        # Class component with __html__
        class Heading:
            @path_nodes
            def __html__(self) -> Node:
                return html(t'<link rel="stylesheet" href="static/styles.css">')

    Args:
        func_or_method: The function or method to wrap. Must return a Node.

    Returns:
        Wrapped callable with same signature that applies make_path_nodes
    """

    @wraps(func_or_method)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Call original function/method to get Node
        result: R = func_or_method(*args, **kwargs)

        # Determine component: function itself or self from method
        if inspect.ismethod(func_or_method) or (args and hasattr(args[0], "__dict__")):
            # Method call - use self (first arg) as component
            component: Any = args[0]
        else:
            # Function call - use function itself as component
            component = func_or_method

        # Apply transformation and return
        return make_path_nodes(result, component)  # type: ignore[return-value]

    return wrapper

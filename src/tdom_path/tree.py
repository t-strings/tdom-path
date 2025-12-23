"""Tree rewriting utilities for component asset path resolution."""

import inspect
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from importlib.resources.abc import Traversable

# Use PurePosixPath instead of PurePath to ensure cross-platform consistency
# Web paths must always use forward slashes (/), never backslashes (\)
# PurePosixPath guarantees POSIX-style paths regardless of OS
from pathlib import PurePosixPath
from typing import Any, Protocol, TypeGuard, ParamSpec

from tdom import Element, Fragment, Node
from tdom_path.webpath import make_path, _normalize_module_name


@dataclass(frozen=True, slots=True)
class AssetReference:
    """Reference to a collected asset with source and destination information.

    This dataclass stores information about assets encountered during rendering,
    enabling build tools to copy them to the output directory. The frozen and
    slotted design ensures hashability for set-based deduplication.

    Attributes:
        source: Traversable instance for reading file contents via .read_bytes()
        module_path: PurePosixPath representing the destination path in build output

    Examples:
        >>> from pathlib import Path, PurePosixPath
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>> # Create asset reference
        >>> source = make_path(Heading, "static/styles.css")
        >>> module_path = PurePosixPath("mysite/components/heading/static/styles.css")
        >>> ref = AssetReference(source=source, module_path=module_path)
        >>>
        >>> # Use in build tool to copy asset
        >>> build_dir = Path("dist")
        >>> content = ref.source.read_bytes()
        >>> dest_path = build_dir / ref.module_path
        >>> # dest_path.write_bytes(content)
    """

    source: Traversable
    module_path: PurePosixPath


@dataclass(frozen=True, slots=True)
class _TraversableWithPath:
    """Pairs a Traversable with its module-relative path.

    This simple container stores both the filesystem Traversable and the
    module-relative path needed for relative path calculation and asset collection.

    Attributes:
        traversable: The Traversable instance for file access
        module_path: Module-relative path (e.g., "mysite/components/heading/static/styles.css")
    """

    traversable: Traversable
    module_path: PurePosixPath

    def __str__(self) -> str:
        """Return the module-relative path as a string."""
        return str(self.module_path)


# Type variables for decorator
P = ParamSpec("P")
type R = Node

# Compile regex once at module load time for performance
_EXTERNAL_URL_PATTERN = re.compile(
    r"^(https?://|//|mailto:|tel:|data:|javascript:|#)", re.IGNORECASE
)


@dataclass(slots=True)
class TraversableElement(Element):
    """Element subclass that allows Traversable attribute values.

    This class extends Element to support Traversable instances in attribute
    values, enabling the tree walker to preserve type information for component
    asset paths through the rendering pipeline.

    The attrs field accepts str, Traversable, or None values. During rendering,
    Traversable values are automatically converted to strings via __str__(),
    producing module-relative path strings in the final HTML output.

    All other behavior is inherited from Element, including __post_init__
    validation and __str__() rendering.

    Examples:
        >>> from importlib.resources.abc import Traversable
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>> # Create element with Traversable href
        >>> path = make_path(Heading, "static/styles.css")
        >>> elem = TraversableElement(
        ...     tag="link",
        ...     attrs={"rel": "stylesheet", "href": path},
        ...     children=[]
        ... )
        >>>
        >>> # Renders to HTML with path auto-converted
        >>> str(elem)[-47:]
        'mysite/components/heading/static/styles.css" />'
    """

    attrs: dict[str, str | Traversable | _TraversableWithPath | None]


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


def _validate_asset_exists(
    asset_path: Traversable, component: Any, attr_name: str
) -> None:
    """Validate that an asset exists.

    Checks if the Traversable asset exists using the .is_file() method.
    Fails immediately with a clear error message if the asset doesn't exist.

    Args:
        asset_path: Traversable instance pointing to the asset
        component: Component instance/class for error context
        attr_name: Attribute name (e.g., "href", "src") for error context

    Raises:
        FileNotFoundError: If the asset file does not exist

    Examples:
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>> # Validate existing asset
        >>> asset_path = make_path(Heading, "static/styles.css")
        >>> _validate_asset_exists(asset_path, Heading, "href")
        >>>
        >>> # Validate missing asset raises FileNotFoundError
        >>> missing_path = make_path(Heading, "static/missing.css")
        >>> try:
        ...     _validate_asset_exists(missing_path, Heading, "href")
        ... except FileNotFoundError as exc:
        ...     assert "missing.css" in str(exc)

    TODO: Consider future validation options:
    - Collect all missing assets and report at end (batch mode)
    - Add strict/lenient mode flag for configurable behavior
    - Log warnings instead of failing (non-blocking mode)
    - All of the above as configuration options (ValidationConfig)
    """
    # Check if the asset file exists
    if not asset_path.is_file():
        # Extract component name for better error messages
        component_name = (
            component.__name__
            if hasattr(component, "__name__")
            else component.__class__.__name__
        )

        # Get module name for additional context
        module_name = getattr(component, "__module__", "unknown")

        # Build clear error message with context
        error_msg = (
            f"Asset not found: '{asset_path.name}' "
            f"(attribute: '{attr_name}', "
            f"component: '{component_name}' in '{module_name}', "
            f"path: {asset_path})"
        )

        raise FileNotFoundError(error_msg)


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
        >>> assert isinstance(result, Element)
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
) -> Element | TraversableElement:
    """Transform element's asset attribute to Traversable.

    Args:
        element: The element to transform (link or script)
        attr_name: The attribute name to transform ("href" or "src")
        component: Component instance/class for make_path() resolution

    Returns:
        New Element or TraversableElement with asset attribute transformed to Traversable
    """
    attr_value = element.attrs.get(attr_name)

    # Only transform if it's a processable local path
    if not _should_process_href(attr_value):
        return element

    # TypeGuard ensures attr_value is str, but add assert for type checker
    assert isinstance(attr_value, str)

    # Create dict that accepts Any values (including Traversable)
    attrs = dict[str, Any](element.attrs)
    asset_path = make_path(component, attr_value)

    # Validate asset existence (fail fast with clear error message)
    _validate_asset_exists(asset_path, component, attr_name)

    # Calculate module-relative path for the asset
    # This will be used for relative path calculations during rendering
    module_name = (
        component.__module__ if hasattr(component, "__module__") else "unknown"
    )
    module_name = _normalize_module_name(module_name)
    module_web_path = module_name.replace(".", "/")
    module_path = PurePosixPath(module_web_path) / attr_value.lstrip("./")

    # Wrap the Traversable with module path for rendering
    wrapped_path = _TraversableWithPath(asset_path, module_path)

    # Store the wrapped asset path
    attrs[attr_name] = wrapped_path

    # Check if any attr value is Traversable or _TraversableWithPath - if so, use TraversableElement
    has_path = any(
        isinstance(v, (Traversable, _TraversableWithPath)) for v in attrs.values()
    )

    if has_path:
        return TraversableElement(
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
    Traversable using make_path(component, attr_value).

    External URLs (http://, https://, //), special schemes (mailto:, tel:,
    data:, javascript:), and anchor-only links (#...) are left unchanged.

    Args:
        target: Root node of the tree to process
        component: Component instance/class for make_path() resolution

    Returns:
        New Node tree with asset attributes converted to Traversable

    Examples:
        >>> from tdom import html
        >>> from mysite.components.heading import Heading
        >>> tree = html(t'''
        ...     <head>
        ...         <link rel="stylesheet" href="static/styles.css">
        ...     </head>
        ... ''')
        >>> new_tree = make_path_nodes(tree, Heading)
    """

    def transform(node: Node) -> Node:
        """Transform asset-bearing elements to use Traversable."""
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

    Defines the interface for calculating how Traversable paths should be
    rendered as strings in the final HTML output. Implementations can provide
    different rendering strategies such as relative paths, absolute paths,
    CDN URLs, etc.

    The protocol requires a single method that takes a source Traversable
    and target output location, returning the string representation to use
    in the rendered HTML.

    Examples:
        >>> from pathlib import PurePosixPath
        >>> from importlib.resources.abc import Traversable
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>> # Use default relative path strategy
        >>> strategy = RelativePathStrategy()
        >>> source = make_path(Heading, "static/styles.css")
        >>> target = PurePosixPath("pages/about.html")
        >>> path_str = strategy.calculate_path(source, target)
        >>> # Returns relative path from pages/about.html to static/styles.css
        >>>
        >>> # Custom strategy with site prefix
        >>> prefixed_strategy = RelativePathStrategy(
        ...     site_prefix=PurePosixPath("mysite/static")
        ... )
        >>> prefixed_strategy.calculate_path(source, target)
        'mysite/static/mysite/components/heading/static/styles.css'
    """

    def calculate_path(self, source: Traversable, target: PurePosixPath) -> str:
        """Calculate string representation for a path in rendered output.

        Args:
            source: The Traversable source path to render
            target: The PurePosixPath target output location

        Returns:
            String representation of the path for use in HTML attributes
        """
        ...


@dataclass(slots=True)
class RelativePathStrategy:
    """Strategy for rendering paths as relative URLs.

    Calculates relative paths from the target output location to the source
    asset location, optionally prepending a site prefix for deployment scenarios
    where assets are served from a subdirectory.

    The strategy works with Traversable objects and calculates relative
    paths based on web directory structure.

    Uses PurePosixPath for all path calculations to ensure cross-platform
    consistency in web path generation.

    Attributes:
        site_prefix: Optional PurePosixPath prefix to prepend to all calculated paths
                    (e.g., PurePosixPath("mysite/static") for subdirectory deployments)
        collected_assets: Set of AssetReference instances for assets encountered during
                         rendering. Build tools can iterate this set after rendering to
                         copy assets to the output directory.

    Examples:
        >>> from pathlib import PurePosixPath
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>> strategy = RelativePathStrategy()
        >>> source = make_path(Heading, "static/styles.css")
        >>> target = PurePosixPath("index.html")
        >>> strategy.calculate_path(source, target)
        'mysite/components/heading/static/styles.css'
        >>> strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
        >>> strategy.calculate_path(source, target)
        'mysite/static/mysite/components/heading/static/styles.css'
        >>> target = PurePosixPath("pages/about.html")
        >>> strategy.calculate_path(source, target)
        'mysite/static/mysite/components/heading/static/styles.css'
    """

    site_prefix: PurePosixPath | None = None
    collected_assets: set[AssetReference] = field(default_factory=set)

    def calculate_path(self, source: Traversable, target: PurePosixPath) -> str:
        """Calculate the relative path from target to source.

        Both source (Traversable) and target (PurePosixPath) represent paths
        to be used for web assets. This method calculates the relative path
        from the target's location to the source, optionally prepending a
        site prefix.

        Args:
            source: The Traversable source asset path
            target: The PurePosixPath target output location (module-relative)

        Returns:
            Relative path string from target to source, with optional prefix

        Examples:
        >>> from mysite.components.heading import Heading
        >>> strategy = RelativePathStrategy()
        >>> this_source = make_path(Heading, "styles.css")
        >>> this_target = PurePosixPath("mysite/components/heading/index.html")
        >>> strategy.calculate_path(this_source, this_target)
        'styles.css'
        >>> this_source = make_path(Heading, "static/styles.css")
        >>> this_target = PurePosixPath("mysite/pages/about.html")
        >>> strategy.calculate_path(this_source, this_target)
        '../components/heading/static/styles.css'
        """
        # Convert to PurePosixPath for calculation
        # If it's _TraversableWithPath, extract the module_path directly
        if isinstance(source, _TraversableWithPath):
            source_path = source.module_path
        else:
            # Fallback for bare Traversable: extract module-relative path from absolute path
            # This is a best-effort approach - won't work for all project structures
            # Absolute path format: /.../.../examples/mysite/components/heading/static/styles.css
            # We want: mysite/components/heading/static/styles.css
            abs_path_str = str(source)
            # Find "examples/" or "tests/" and take everything after it
            if "/examples/" in abs_path_str:
                module_relative = abs_path_str.split("/examples/", 1)[1]
                source_path = PurePosixPath(module_relative)
            elif "/tests/" in abs_path_str:
                module_relative = abs_path_str.split("/tests/", 1)[1]
                source_path = PurePosixPath(module_relative)
            else:
                # Last resort: use absolute path
                source_path = PurePosixPath(abs_path_str)

        # If site_prefix is provided, prepend it to the source path
        # This is useful for deploying to subdirectories (e.g., GitHub Pages /repo/)
        if self.site_prefix:
            return str(self.site_prefix / source_path)

        # Calculate relative path from target's parent directory to source
        # Why target.parent? Because target is a file (e.g., pages/about.html),
        # and we need the directory it's in (pages/) to calculate the relative path
        target_dir = target.parent

        # Use pathlib's relative_to with walk_up=True for proper relative path calculation
        # walk_up=True allows climbing up directories with ../ notation
        # Example: from pages/about.html to components/heading/static/styles.css
        # becomes: ../components/heading/static/styles.css
        try:
            relative_path = source_path.relative_to(target_dir, walk_up=True)
            return str(relative_path)
        except ValueError:
            # If relative_to fails (rare edge case), return source path as-is
            return str(source_path)


def _render_transform_node(
    node: Node, target: PurePosixPath, strategy: RenderStrategy
) -> Node:
    """Transform TraversableElement nodes to Element nodes with string paths.

    Helper function that processes a single node, converting TraversableElement
    instances with Traversable attributes into regular Element instances
    with those paths rendered as strings.

    Args:
        node: The node to transform
        target: Target output location for relative path calculation
        strategy: RenderStrategy for path calculation

    Returns:
        Transformed Element node, or original node if no transformation needed
    """
    # Only process TraversableElement instances
    if not isinstance(node, TraversableElement):
        return node

    # Check if any attribute contains a Traversable or _TraversableWithPath
    has_path_attr = any(
        isinstance(value, (Traversable, _TraversableWithPath))
        for value in node.attrs.values()
    )

    # If no Traversable attributes, return unchanged
    if not has_path_attr:
        return node

    # Transform Traversable/wrapped attributes to strings using strategy
    new_attrs: dict[str, str | None] = {}
    for attr_name, attr_value in node.attrs.items():
        if isinstance(attr_value, _TraversableWithPath):
            # Extract source Traversable and module path from NamedTuple
            source = attr_value.traversable
            module_path = attr_value.module_path

            # Create AssetReference and add to strategy's collected_assets
            asset_ref = AssetReference(source=source, module_path=module_path)

            # Add to collected_assets set (deduplicates automatically)
            # Only add if strategy has collected_assets attribute (e.g., RelativePathStrategy)
            if hasattr(strategy, "collected_assets"):
                strategy.collected_assets.add(asset_ref)  # type: ignore[attr-defined]

            # Calculate string path using strategy (pass the unwrapped Traversable)
            new_attrs[attr_name] = strategy.calculate_path(source, target)
        elif isinstance(attr_value, Traversable):
            # Bare Traversable (shouldn't happen in normal use, but handle it)
            new_attrs[attr_name] = strategy.calculate_path(attr_value, target)
        else:
            # Preserve non-Traversable attributes as-is
            new_attrs[attr_name] = attr_value  # type: ignore

    # Return new Element (NOT TraversableElement) with string attributes
    return Element(
        tag=node.tag,
        attrs=new_attrs,
        children=node.children,
    )


def render_path_nodes(
    tree: Node, target: PurePosixPath, strategy: RenderStrategy | None = None
) -> Node:
    """Render TraversableElement nodes to Element nodes with relative path strings.

    Walks the Node tree, detects TraversableElement instances containing Traversable
    attribute values, and transforms them into regular Element instances with
    those paths rendered as strings using the provided strategy.

    This function is the final rendering step after make_path_nodes() has
    converted asset paths to Traversable instances. It calculates the
    appropriate string representation for each path based on the target
    output location.

    The function processes ANY attribute containing a Traversable value,
    not just href and src. This enables flexible asset path handling for
    custom attributes.

    Maintains immutability by creating new nodes only when transformations
    occur. Returns the same object reference when no TraversableElement nodes are
    found (optimization).

    Args:
        tree: Root node of the tree to process
        target: PurePosixPath target output location (e.g., "mysite/pages/index.html")
        strategy: Optional RenderStrategy for path calculation.
                 Defaults to RelativePathStrategy() if None.

    Returns:
        New Node tree with TraversableElement nodes transformed to Element nodes
        containing string path attributes, or the same object if no changes needed

    Examples:
        >>> from pathlib import PurePosixPath
        >>> from tdom import html
        >>> from tdom_path import make_path_nodes, render_path_nodes
        >>> from tdom_path.tree import RelativePathStrategy
        >>> from mysite.components.heading import Heading
        >>> # Step 1: Create tree with TraversableElement nodes
        >>> tree = html(t'''
        ...     <head>
        ...         <link rel="stylesheet" href="static/styles.css">
        ...     </head>
        ... ''')
        >>> path_tree = make_path_nodes(tree, Heading)
        >>>
        >>> # Step 2: Render TraversableElement nodes to Element with relative paths
        >>> target = PurePosixPath("mysite/pages/about.html")
        >>> rendered = render_path_nodes(path_tree, target)
        >>> # Link now has href="../../components/heading/static/styles.css"
        >>>
        >>> # With custom strategy (site prefix)
        >>> this_strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
        >>> this_rendered = render_path_nodes(path_tree, target, strategy=this_strategy)
        >>> this_rendered.children[1].children[1].attrs["href"]
        'mysite/static/mysite/components/heading/static/styles.css'
    """
    # Default to RelativePathStrategy if no strategy provided
    if strategy is None:
        strategy = RelativePathStrategy()

    # Use _walk_tree with _render_transform_node helper
    return _walk_tree(tree, lambda node: _render_transform_node(node, target, strategy))


def path_nodes[**P](
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

"""Tree rewriting utilities for component asset path resolution."""

import inspect
import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from importlib.resources.abc import Traversable
from typing import Any, ParamSpec, TypeGuard

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
class TraversableElement(Element):
    """Element subclass that allows Traversable attribute values.

    This class extends Element to support Traversable instances in attribute
    values, enabling the tree walker to preserve type information for component
    asset paths through the rendering pipeline.

    The attrs field accepts str, Traversable, or None values. During rendering,
    Traversable values are automatically converted to strings via __str__() and
    __fspath__(), producing filesystem path strings in the final HTML output.

    All other behavior is inherited from Element, including __post_init__
    validation and __str__() rendering.

    Examples:
        >>> from importlib.resources.abc import Traversable
        >>> from tdom_path.webpath import make_path
        >>> from mysite.components.heading import Heading
        >>>
        >>> # Create element with Traversable href
        >>> path = make_path(Heading, "static/styles.css")
        >>> elem = TraversableElement(
        ...     tag="link",
        ...     attrs={"rel": "stylesheet", "href": path},
        ...     children=[]
        ... )
        >>>
        >>> # Renders to HTML with path auto-converted
        >>> str(elem)
        '<link rel="stylesheet" href="/path/to/static/styles.css" />'
    """

    attrs: dict[str, str | Traversable | None]


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
    attrs[attr_name] = make_path(component, attr_value)

    # Check if any attr value is Traversable - if so, use TraversableElement
    has_traversable = any(isinstance(v, Traversable) for v in attrs.values())

    if has_traversable:
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
        >>>
        >>> # Original tree with string href
        >>> tree = html(t'''
        ...     <head>
        ...         <link rel="stylesheet" href="static/styles.css">
        ...     </head>
        ... ''')
        >>>
        >>> # Transform to use Traversable
        >>> new_tree = make_path_nodes(tree, Heading)
        >>> # new_tree now has Traversable in link's href
    """

    def walk(node: Node) -> Node:
        """Recursively walk tree and transform asset-bearing elements."""
        match node:
            # Transform <link> elements with href
            case Element(tag="link"):
                return _transform_asset_element(node, "href", component)

            # Transform <script> elements with src
            case Element(tag="script"):
                return _transform_asset_element(node, "src", component)

            # Other elements with children - recurse
            case Element(children=children) if children:
                new_children = [walk(child) for child in children]
                # Only create new Element if children actually changed
                if any(new is not old for new, old in zip(new_children, children)):
                    return Element(
                        tag=node.tag,
                        attrs=node.attrs.copy() if node.attrs else {},
                        children=new_children,
                    )
                return node

            # Fragment nodes with children - recurse
            case Fragment(children=children) if children:
                new_children = [walk(child) for child in children]
                # Only create new Fragment if children actually changed
                if any(new is not old for new, old in zip(new_children, children)):
                    return Fragment(children=new_children)
                return node

            # All other nodes (Text, Comment, leaf elements, etc.)
            case _:
                return node

    return walk(target)


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

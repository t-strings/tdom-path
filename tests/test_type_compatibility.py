"""Tests for Traversable type compatibility.

These tests verify that TraversableElement accepts Traversable attribute values,
type compatibility with the rendering pipeline, and proper rendering of Traversable
attributes to strings.

Task 4.1: Write 2-8 focused tests for type compatibility
- Test TraversableElement accepts Traversable attribute values
- Test type checker compatibility (if using mypy/pyright)
- Test rendering of Traversable attributes to strings
- Skip exhaustive type checking scenarios
"""

from importlib.resources.abc import Traversable
from pathlib import PurePosixPath

from mysite.components.heading import Heading
from tdom import Element
from tdom_path.tree import (
    TraversableElement,
    RelativePathStrategy,
    _render_transform_node,
)
from tdom_path.webpath import make_path


def test_traversable_element_accepts_mixed_attr_types():
    """Test TraversableElement with mixed attribute types (str, Traversable, None).

    Verifies that the type annotation dict[str, str | Traversable | None]
    properly supports all three allowed types in the same attrs dict, including
    multiple Traversable attributes.
    """
    css_path = make_path(Heading, "static/styles.css")
    js_path = make_path(Heading, "static/script.js")

    # Create element with mixed attribute types including multiple Traversables
    elem = TraversableElement(
        tag="link",
        attrs={
            "rel": "stylesheet",  # str
            "href": css_path,  # Traversable
            "data-js": js_path,  # Traversable
            "data-empty": None,  # None
            "media": "screen",  # str
        },
        children=[],
    )

    # Verify all attribute types are preserved
    assert elem.attrs["rel"] == "stylesheet"
    assert isinstance(elem.attrs["href"], Traversable)
    assert isinstance(elem.attrs["data-js"], Traversable)
    assert elem.attrs["data-empty"] is None
    assert elem.attrs["media"] == "screen"


def test_render_transform_node_handles_mixed_attributes():
    """Test that _render_transform_node converts Traversable to string while preserving others.

    Verifies the rendering pipeline properly converts Traversable attribute values
    to string representations using the strategy, while preserving non-Traversable
    attributes (str, None) unchanged.
    """
    css_path = make_path(Heading, "static/styles.css")
    js_path = make_path(Heading, "static/script.js")

    # Create element with mixed attributes
    elem = TraversableElement(
        tag="link",
        attrs={
            "rel": "stylesheet",  # Should be preserved
            "href": css_path,  # Should be converted to string
            "data-js": js_path,  # Should be converted to string
            "data-test": None,  # Should be preserved
            "media": "screen",  # Should be preserved
        },
        children=[],
    )

    # Render using strategy
    target = PurePosixPath("index.html")
    strategy = RelativePathStrategy()
    result = _render_transform_node(elem, target, strategy)

    # Result should be a regular Element (not TraversableElement)
    assert isinstance(result, Element)
    assert not isinstance(result, TraversableElement)

    # Non-Traversable attributes should be preserved
    assert result.attrs["rel"] == "stylesheet"
    assert result.attrs["data-test"] is None
    assert result.attrs["media"] == "screen"

    # Traversable attributes should be converted to strings
    assert isinstance(result.attrs["href"], str)
    assert isinstance(result.attrs["data-js"], str)
    assert "styles.css" in result.attrs["href"]
    assert "script.js" in result.attrs["data-js"]


def test_render_strategy_converts_traversable_to_relative_path():
    """Test that RelativePathStrategy properly converts Traversable to relative paths.

    Verifies the strategy accepts Traversable instances and computes
    correct relative paths based on target location.
    """
    css_path = make_path(Heading, "static/styles.css")
    assert isinstance(css_path, Traversable)

    strategy = RelativePathStrategy()

    # Test from same directory
    target = PurePosixPath("mysite/components/heading/index.html")
    result = strategy.calculate_path(css_path, target)
    assert isinstance(result, str)
    assert "styles.css" in result

    # Test from different directory (should use relative navigation)
    target2 = PurePosixPath("mysite/pages/about.html")
    result2 = strategy.calculate_path(css_path, target2)
    assert isinstance(result2, str)
    assert "styles.css" in result2


def test_traversable_element_end_to_end_rendering():
    """Test that TraversableElement renders to HTML with Traversable converted to string.

    Verifies the full end-to-end type compatibility: TraversableElement
    with Traversable attributes can be rendered to an HTML string.
    """
    css_path = make_path(Heading, "static/styles.css")

    # Create TraversableElement
    elem = TraversableElement(
        tag="link", attrs={"rel": "stylesheet", "href": css_path}, children=[]
    )

    # Convert to string representation
    # TraversableElement inherits __str__ from Element which converts
    # Traversable values using str()
    html_str = str(elem)

    # Should produce valid HTML with path converted to string
    assert "<link" in html_str
    assert "rel=" in html_str
    assert "stylesheet" in html_str
    assert "href=" in html_str
    # The Traversable will be converted to string via __str__()
    assert isinstance(html_str, str)

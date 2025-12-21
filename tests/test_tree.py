"""Tests for make_path_nodes tree rewriting functionality.

These tests use HTML template strings for more readable test cases.
Focus on core functionality:
- Tree walking and element transformation
- Detection of <link> and <script> tags
- Skipping external URLs and special schemes
- Decorator support for function and class components
"""

from pathlib import PurePosixPath
from importlib.resources.abc import Traversable

from aria_testing import get_by_tag_name, get_all_by_tag_name
from tdom import Element, Fragment, Text, Comment, html
from mysite.components.heading import Heading
from tdom_path import make_path_nodes, path_nodes
from tdom_path.tree import (
    TraversableElement,
    _walk_tree,
    _should_process_href,
    _transform_asset_element,
    _render_transform_node,
    render_path_nodes,
    RelativePathStrategy,
    RenderStrategy,
    _validate_asset_exists,
)
from tdom_path.webpath import make_path


# ============================================================================
# Helper Function Unit Tests
# ============================================================================


def test_should_process_href_with_local_paths():
    """Test _should_process_href returns True for local paths."""
    from tdom_path.tree import _should_process_href

    # Local relative paths should be processed
    assert _should_process_href("static/styles.css") is True
    assert _should_process_href("./static/styles.css") is True
    assert _should_process_href("../shared/styles.css") is True
    assert _should_process_href("assets/images/logo.png") is True


def test_should_process_href_with_external_urls():
    """Test _should_process_href returns False for external URLs."""
    from tdom_path.tree import _should_process_href

    # External URLs should NOT be processed
    assert _should_process_href("http://example.com/style.css") is False
    assert _should_process_href("https://cdn.example.com/style.css") is False
    assert _should_process_href("//cdn.example.com/style.css") is False
    assert _should_process_href("HTTP://EXAMPLE.COM/STYLE.CSS") is False  # Case insensitive


def test_should_process_href_with_special_schemes():
    """Test _should_process_href returns False for special schemes."""
    from tdom_path.tree import _should_process_href

    # Special schemes should NOT be processed
    assert _should_process_href("mailto:user@example.com") is False
    assert _should_process_href("tel:+1234567890") is False
    assert _should_process_href("data:image/png;base64,abc123") is False
    assert _should_process_href("javascript:void(0)") is False
    assert _should_process_href("#section") is False
    assert _should_process_href("MAILTO:USER@EXAMPLE.COM") is False  # Case insensitive


def test_should_process_href_with_empty_values():
    """Test _should_process_href returns False for empty/None values."""
    from tdom_path.tree import _should_process_href

    # Empty or None values should NOT be processed
    assert _should_process_href(None) is False
    assert _should_process_href("") is False


def test_should_process_href_with_non_string():
    """Test _should_process_href returns False for non-string values."""
    from tdom_path.tree import _should_process_href

    # Non-string values should NOT be processed
    assert _should_process_href(123) is False  # type: ignore
    assert _should_process_href(PurePosixPath("static/style.css")) is False  # type: ignore


def test_transform_asset_element_with_local_href():
    """Test _transform_asset_element transforms local href to Traversable."""
    from tdom_path.tree import _transform_asset_element

    elem = Element(
        tag="link",
        attrs={"rel": "stylesheet", "href": "static/styles.css"},
        children=[]
    )

    result = _transform_asset_element(elem, "href", Heading)

    # Should return TraversableElement with Traversable href
    assert isinstance(result, TraversableElement)
    assert isinstance(result.attrs["href"], Traversable)
    assert str(result.attrs["href"]) == "mysite/components/heading/static/styles.css"
    # Other attributes preserved
    assert result.attrs["rel"] == "stylesheet"


def test_transform_asset_element_with_external_href():
    """Test _transform_asset_element leaves external URLs unchanged."""
    from tdom_path.tree import _transform_asset_element

    elem = Element(
        tag="link",
        attrs={"rel": "stylesheet", "href": "https://cdn.example.com/style.css"},
        children=[]
    )

    result = _transform_asset_element(elem, "href", Heading)

    # Should return original Element unchanged (not TraversableElement)
    assert result is elem
    assert isinstance(result, Element)
    assert not isinstance(result, TraversableElement)
    assert result.attrs["href"] == "https://cdn.example.com/style.css"


def test_transform_asset_element_with_script_src():
    """Test _transform_asset_element works with script src attribute."""
    from tdom_path.tree import _transform_asset_element

    elem = Element(
        tag="script",
        attrs={"src": "static/app.js", "defer": "true"},
        children=[]
    )

    result = _transform_asset_element(elem, "src", Heading)

    # Should return TraversableElement with Traversable src
    assert isinstance(result, TraversableElement)
    assert isinstance(result.attrs["src"], Traversable)
    assert str(result.attrs["src"]) == "mysite/components/heading/static/app.js"
    # Other attributes preserved
    assert result.attrs["defer"] == "true"


def test_transform_asset_element_with_missing_attribute():
    """Test _transform_asset_element handles missing attribute gracefully."""
    from tdom_path.tree import _transform_asset_element

    # Link without href attribute
    elem = Element(
        tag="link",
        attrs={"rel": "stylesheet"},
        children=[]
    )

    result = _transform_asset_element(elem, "href", Heading)

    # Should return original element unchanged
    assert result is elem


def test_transform_asset_element_preserves_children():
    """Test _transform_asset_element preserves element children."""
    from tdom_path.tree import _transform_asset_element

    child_text = Text("Loading...")
    elem = Element(
        tag="script",
        attrs={"src": "static/app.js"},
        children=[child_text]
    )

    result = _transform_asset_element(elem, "src", Heading)

    # Should preserve children
    assert len(result.children) == 1
    assert result.children[0] is child_text


def test_render_transform_node_with_path_element():
    """Test _render_transform_node transforms TraversableElement to Element."""
    from tdom_path.tree import _render_transform_node

    css_path = make_path(Heading, "static/styles.css")
    strategy = RelativePathStrategy()
    target = PurePosixPath("mysite/components/heading/index.html")

    node = TraversableElement(
        tag="link",
        attrs={"rel": "stylesheet", "href": css_path},
        children=[]
    )

    result = _render_transform_node(node, target, strategy)

    # Should return Element (not TraversableElement)
    assert isinstance(result, Element)
    assert not isinstance(result, TraversableElement)
    # Traversable should be converted to string
    assert isinstance(result.attrs["href"], str)
    assert result.attrs["href"] == "static/styles.css"
    # Other attributes preserved
    assert result.attrs["rel"] == "stylesheet"


def test_render_transform_node_with_regular_element():
    """Test _render_transform_node leaves regular Element unchanged."""
    from tdom_path.tree import _render_transform_node

    strategy = RelativePathStrategy()
    target = PurePosixPath("index.html")

    node = Element(
        tag="div",
        attrs={"class": "container"},
        children=[]
    )

    result = _render_transform_node(node, target, strategy)

    # Should return same node unchanged
    assert result is node


def test_render_transform_node_with_path_element_no_paths():
    """Test _render_transform_node leaves TraversableElement without Traversable unchanged."""
    from tdom_path.tree import _render_transform_node

    strategy = RelativePathStrategy()
    target = PurePosixPath("index.html")

    # TraversableElement but no Traversable attributes
    node = TraversableElement(
        tag="link",
        attrs={"rel": "stylesheet", "href": "https://cdn.example.com/style.css"},
        children=[]
    )

    result = _render_transform_node(node, target, strategy)

    # Should return same node unchanged
    assert result is node


def test_render_transform_node_multiple_path_attrs():
    """Test _render_transform_node transforms multiple Traversable attributes."""
    from tdom_path.tree import _render_transform_node

    path1 = make_path(Heading, "static/file1.css")
    path2 = make_path(Heading, "static/file2.js")
    strategy = RelativePathStrategy()
    target = PurePosixPath("mysite/pages/index.html")

    node = TraversableElement(
        tag="custom",
        attrs={
            "data-css": path1,
            "data-js": path2,
            "rel": "custom"
        },
        children=[]
    )

    result = _render_transform_node(node, target, strategy)

    # Should transform both Traversable attributes
    assert isinstance(result, Element)
    assert not isinstance(result, TraversableElement)
    assert isinstance(result.attrs["data-css"], str)
    assert isinstance(result.attrs["data-js"], str)
    assert "components/heading/static/file1.css" in result.attrs["data-css"]
    assert "components/heading/static/file2.js" in result.attrs["data-js"]
    # String attribute preserved
    assert result.attrs["rel"] == "custom"


def test_render_transform_node_with_custom_strategy():
    """Test _render_transform_node uses provided strategy."""
    from tdom_path.tree import _render_transform_node

    css_path = make_path(Heading, "static/styles.css")
    strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
    target = PurePosixPath("index.html")

    node = TraversableElement(
        tag="link",
        attrs={"rel": "stylesheet", "href": css_path},
        children=[]
    )

    result = _render_transform_node(node, target, strategy)

    # Should use custom strategy with site prefix
    assert isinstance(result, Element)
    assert isinstance(result.attrs["href"], str)
    assert result.attrs["href"].startswith("mysite/static")


# ============================================================================
# _walk_tree() Helper Tests (Task Group 1)
# ============================================================================


def test_walk_tree_transformation_and_immutability():
    """Test _walk_tree() applies transformations while preserving immutability."""
    original = html(t"""
        <div class="container">
            <p id="test">Hello</p>
            <>
                <span>World</span>
            </>
        </div>
    """)

    # Transform function that modifies nested p elements
    visited_tags = []
    def modify_p(node):
        if isinstance(node, Element):
            visited_tags.append(node.tag)
            if node.tag == "p":
                return Element(tag="p", attrs={"id": "modified"}, children=node.children)
        return node

    result = _walk_tree(original, modify_p)

    # Verify all Element tags were visited (basic traversal)
    assert "div" in visited_tags
    assert "p" in visited_tags
    assert "span" in visited_tags

    # Verify immutability - original should be unchanged
    p_original = get_by_tag_name(original, "p")
    assert p_original.attrs["id"] == "test"

    # Verify transformation - result should have modified version
    p_result = get_by_tag_name(result, "p")
    assert p_result.attrs["id"] == "modified"

    # Parent should be a new object (because child changed)
    assert result is not original


def test_walk_tree_optimization_unchanged():
    """Test _walk_tree() returns same object when no transformations applied."""
    tree = html(t"""
        <div>
            Hello
            <!--comment-->
            <p></p>
        </div>
    """)

    # Identity transform - returns node unchanged
    def identity(node):
        return node

    result = _walk_tree(tree, identity)

    # Should return exact same object reference (optimization)
    assert result is tree


# ============================================================================
# TraversableElement Class Tests (Task Group 1)
# ============================================================================


def test_path_element_behavior():
    """Test TraversableElement attributes, inheritance, and rendering."""
    import pytest

    css_path = make_path(Heading, "static/styles.css")
    js_path = make_path(Heading, "static/script.js")

    # Test mixed attr types (str, Traversable, None)
    elem = TraversableElement(
        tag="link",
        attrs={
            "rel": "stylesheet",
            "href": css_path,
            "type": "text/css",
            "media": None
        },
        children=[]
    )

    assert elem.tag == "link"
    assert isinstance(elem.attrs["href"], Traversable)
    assert elem.attrs["href"] == css_path
    assert isinstance(elem.attrs["rel"], str)
    assert elem.attrs["media"] is None

    # Test Element inheritance and dataclass configuration
    assert isinstance(elem, Element)
    assert not hasattr(elem, "__dict__")  # slots=True

    # Test immutability pattern
    new_elem = TraversableElement(tag="script", attrs=elem.attrs, children=elem.children)
    assert new_elem.tag == "script"
    assert elem.tag == "link"  # Original unchanged

    # Test validation from Element
    with pytest.raises(ValueError, match="Element tag cannot be empty"):
        TraversableElement(tag="", attrs={}, children=[])


# ============================================================================
# RenderStrategy Protocol and RelativePathStrategy Tests (Task Group 2)
# ============================================================================


def test_relative_path_strategy_calculations():
    """Test RelativePathStrategy calculates relative paths correctly across various scenarios."""
    from tdom_path.tree import RelativePathStrategy

    strategy = RelativePathStrategy()

    # Same directory: mysite/components/heading/index.html -> mysite/components/heading/static/styles.css
    source = make_path(Heading, "static/styles.css")
    target = PurePosixPath("mysite/components/heading/index.html")
    result = strategy.calculate_path(source, target)
    assert result == "static/styles.css"

    # Parent directory navigation: mysite/pages/about.html -> mysite/components/heading/static/styles.css
    source = make_path(Heading, "static/styles.css")
    target = PurePosixPath("mysite/pages/about.html")
    result = strategy.calculate_path(source, target)
    assert ".." in result  # Should use ../
    assert "components/heading/static/styles.css" in result

    # Nested paths: mysite/index.html -> mysite/components/heading/static/css/main.css
    source = make_path(Heading, "static/css/main.css")
    target = PurePosixPath("mysite/index.html")
    result = strategy.calculate_path(source, target)
    assert "components/heading/static/css/main.css" in result

    # Same component directory: mysite/components/heading/index.html -> mysite/components/heading/styles.css
    source = make_path(Heading, "styles.css")
    target = PurePosixPath("mysite/components/heading/index.html")
    result = strategy.calculate_path(source, target)
    assert result == "styles.css"

    # Cross directory: mysite/pages/docs/guide.html -> mysite/components/heading/assets/js/app.js
    source = make_path(Heading, "assets/js/app.js")
    target = PurePosixPath("mysite/pages/docs/guide.html")
    result = strategy.calculate_path(source, target)
    assert ".." in result
    assert "components/heading/assets/js/app.js" in result


def test_relative_path_strategy_with_site_prefix():
    """Test RelativePathStrategy prepends site_prefix."""
    from tdom_path.tree import RelativePathStrategy

    strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))

    source_path = make_path(Heading, "static/styles.css")
    target = PurePosixPath("index.html")

    result = strategy.calculate_path(source_path, target)

    # Should start with the site prefix
    assert result.startswith("mysite/static")


# ============================================================================
# render_path_nodes() Tests (Task Group 3)
# ============================================================================


def test_render_path_nodes_detection_and_transformation():
    """Test render_path_nodes() detects TraversableElement and transforms to Element."""
    # Create tree with TraversableElement containing Traversable
    css_path = make_path(Heading, "static/styles.css")
    js_path = make_path(Heading, "static/app.js")

    tree = Element(
        tag="html",
        attrs={},
        children=[
            Element(
                tag="head",
                attrs={},
                children=[
                    TraversableElement(
                        tag="link",
                        attrs={"rel": "stylesheet", "href": css_path},
                        children=[]
                    ),
                    TraversableElement(
                        tag="script",
                        attrs={"src": js_path},
                        children=[]
                    )
                ]
            )
        ]
    )

    target = PurePosixPath("mysite/pages/index.html")
    result = render_path_nodes(tree, target)

    # Verify TraversableElements transformed to regular Elements
    head = get_by_tag_name(result, "head")
    link = get_by_tag_name(head, "link")
    script = get_by_tag_name(head, "script")

    # Should be regular Element, not TraversableElement
    assert isinstance(link, Element)
    assert not isinstance(link, TraversableElement)
    assert isinstance(script, Element)
    assert not isinstance(script, TraversableElement)

    # Traversable attributes should be replaced with strings
    assert isinstance(link.attrs["href"], str)
    assert isinstance(script.attrs["src"], str)

    # Verify relative path calculation
    assert ".." in link.attrs["href"]
    assert "components/heading/static/styles.css" in link.attrs["href"]
    assert ".." in script.attrs["src"]
    assert "components/heading/static/app.js" in script.attrs["src"]


def test_render_path_nodes_with_default_strategy():
    """Test render_path_nodes() uses default RelativePathStrategy."""
    css_path = make_path(Heading, "static/styles.css")

    tree = TraversableElement(
        tag="link",
        attrs={"rel": "stylesheet", "href": css_path},
        children=[]
    )

    target = PurePosixPath("mysite/components/heading/index.html")
    result = render_path_nodes(tree, target)

    # Should use relative path from same directory
    assert isinstance(result, Element)
    assert not isinstance(result, TraversableElement)
    assert result.attrs["href"] == "static/styles.css"


def test_render_path_nodes_with_custom_strategy():
    """Test render_path_nodes() accepts custom strategy parameter."""
    css_path = make_path(Heading, "static/styles.css")

    tree = TraversableElement(
        tag="link",
        attrs={"rel": "stylesheet", "href": css_path},
        children=[]
    )

    # Custom strategy with site prefix
    strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
    target = PurePosixPath("index.html")
    result = render_path_nodes(tree, target, strategy=strategy)

    # Should use custom strategy with prefix
    assert isinstance(result, Element)
    assert isinstance(result.attrs["href"], str)
    assert result.attrs["href"].startswith("mysite/static")


def test_render_path_nodes_optimization_no_path_elements():
    """Test render_path_nodes() returns same object when no TraversableElements."""
    tree = Element(
        tag="div",
        attrs={},
        children=[
            Element(tag="p", attrs={}, children=[Text("Hello")]),
            Text("World")
        ]
    )

    target = PurePosixPath("index.html")
    result = render_path_nodes(tree, target)

    # Should return same object reference (optimization)
    assert result is tree


def test_render_path_nodes_mixed_tree():
    """Test render_path_nodes() handles mixed Element and TraversableElement tree."""
    css_path = make_path(Heading, "static/styles.css")

    tree = Element(
        tag="html",
        attrs={},
        children=[
            Element(
                tag="head",
                attrs={},
                children=[
                    TraversableElement(
                        tag="link",
                        attrs={"rel": "stylesheet", "href": css_path},
                        children=[]
                    ),
                    Element(
                        tag="title",
                        attrs={},
                        children=[Text("Test Page")]
                    )
                ]
            ),
            Element(
                tag="body",
                attrs={"class": "main"},
                children=[
                    Element(tag="h1", attrs={}, children=[Text("Hello")])
                ]
            )
        ]
    )

    target = PurePosixPath("mysite/pages/index.html")
    result = render_path_nodes(tree, target)

    # Verify link transformed
    head = get_by_tag_name(result, "head")
    link = get_by_tag_name(head, "link")
    assert isinstance(link, Element)
    assert not isinstance(link, TraversableElement)
    assert isinstance(link.attrs["href"], str)

    # Verify other elements unchanged
    title = get_by_tag_name(head, "title")
    assert isinstance(title.children[0], Text)
    assert title.children[0].text == "Test Page"

    body = get_by_tag_name(result, "body")
    assert body.attrs["class"] == "main"

    h1 = get_by_tag_name(body, "h1")
    assert isinstance(h1.children[0], Text)
    assert h1.children[0].text == "Hello"


def test_render_path_nodes_multiple_path_attributes():
    """Test render_path_nodes() processes ANY Traversable attribute, not just href/src."""
    # Create TraversableElement with multiple Traversable attributes
    path1 = make_path(Heading, "static/file1.css")
    path2 = make_path(Heading, "static/file2.js")

    tree = TraversableElement(
        tag="custom",
        attrs={
            "data-style": path1,
            "data-script": path2,
            "rel": "custom"
        },
        children=[]
    )

    target = PurePosixPath("mysite/pages/index.html")
    result = render_path_nodes(tree, target)

    # Both Traversable attributes should be transformed
    assert isinstance(result, Element)
    assert not isinstance(result, TraversableElement)
    assert isinstance(result.attrs["data-style"], str)
    assert isinstance(result.attrs["data-script"], str)
    assert "components/heading/static/file1.css" in result.attrs["data-style"]
    assert "components/heading/static/file2.js" in result.attrs["data-script"]
    # String attribute preserved
    assert result.attrs["rel"] == "custom"


# ============================================================================
# Tree Walker Integration Tests (Task Group 2)
# ============================================================================


def test_tree_walker_element_type_creation():
    """Test TraversableElement vs Element creation based on attribute transformations."""
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="https://cdn.example.com/external.css">
                <link rel="stylesheet" href="static/local.css">
                <script src="static/script.js"></script>
            </head>
            <body>
                <div>
                    <p>Content</p>
                </div>
            </body>
        </html>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # External link should be regular Element (no transformation)
    head = get_by_tag_name(new_tree, "head")
    links = get_all_by_tag_name(head, "link")
    external_link = links[0]
    assert isinstance(external_link, Element)
    assert not isinstance(external_link, TraversableElement)
    assert isinstance(external_link.attrs["href"], str)
    assert external_link.attrs["href"] == "https://cdn.example.com/external.css"

    # Local link should be TraversableElement with full module-relative path
    local_link = links[1]
    assert isinstance(local_link, TraversableElement)
    assert isinstance(local_link.attrs["href"], Traversable)
    assert str(local_link.attrs["href"]) == "mysite/components/heading/static/local.css"

    # Script should be TraversableElement with full module-relative path
    script = get_by_tag_name(new_tree, "script")
    assert isinstance(script, TraversableElement)
    assert isinstance(script.attrs["src"], Traversable)
    assert str(script.attrs["src"]) == "mysite/components/heading/static/script.js"

    # Parent elements without asset transformations should be regular Elements
    body = get_by_tag_name(new_tree, "body")
    div = get_by_tag_name(body, "div")
    assert isinstance(head, Element)
    assert not isinstance(head, TraversableElement)
    assert isinstance(body, Element)
    assert not isinstance(body, TraversableElement)
    assert isinstance(div, Element)
    assert not isinstance(div, TraversableElement)


# ============================================================================
# Integration Tests (Task Group 3)
# ============================================================================


def test_integration_end_to_end_rendering():
    """Test end-to-end: TraversableElement creation and HTML rendering."""
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="static/styles.css">
                <script src="static/app.js"></script>
            </head>
            <body>
                <h1>Test Page</h1>
            </body>
        </html>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # Verify TraversableElement instances created with full paths
    link = get_by_tag_name(new_tree, "link")
    script = get_by_tag_name(new_tree, "script")
    assert isinstance(link, TraversableElement)
    assert isinstance(script, TraversableElement)
    assert str(link.attrs["href"]) == "mysite/components/heading/static/styles.css"
    assert str(script.attrs["src"]) == "mysite/components/heading/static/app.js"

    # Verify rendering with Traversable auto-conversion includes module paths
    html_output = str(new_tree)
    assert "mysite/components/heading/static/styles.css" in html_output
    assert "mysite/components/heading/static/app.js" in html_output
    assert "<h1>Test Page</h1>" in html_output


def test_integration_decorator_with_traversable_element():
    """Test @path_nodes decorator creates TraversableElement instances."""

    @path_nodes
    def test_component():
        return html(t"""
            <head>
                <link rel="stylesheet" href="static/styles.css">
            </head>
        """)

    result = test_component()
    link = get_by_tag_name(result, "link")

    assert isinstance(link, TraversableElement)
    assert isinstance(link.attrs["href"], Traversable)
    # Verify full module-relative path includes test function's module
    assert "static/styles.css" in str(link.attrs["href"])


def test_integration_not_exported_from_main_module():
    """Test that TraversableElement is NOT exposed in public API."""
    import tdom_path

    assert "TraversableElement" not in tdom_path.__all__
    assert not hasattr(tdom_path, "TraversableElement")

    # Verify it's only accessible from tree module
    from tdom_path.tree import TraversableElement as TreeTraversableElement
    assert TreeTraversableElement is not None


# ============================================================================
# make_path_nodes() URL Skipping Tests
# ============================================================================


def test_make_path_nodes_url_skipping():
    """Test that external URLs and special schemes are not transformed."""
    tree = html(t"""
        <head>
            <link rel="stylesheet" href="http://cdn.example.com/style.css">
            <link rel="stylesheet" href="https://cdn.example.com/style.css">
            <link rel="stylesheet" href="//cdn.example.com/style.css">
            <link rel="me" href="mailto:user@example.com">
            <link rel="me" href="tel:+1234567890">
            <link rel="icon" href="data:image/png;base64,abc123">
            <link rel="canonical" href="#section">
            <script src="javascript:void(0)"></script>
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # All links and scripts should remain as strings (not transformed)
    head = get_by_tag_name(new_tree, "head")
    links = get_all_by_tag_name(head, "link")
    scripts = get_all_by_tag_name(head, "script")

    # Verify all are regular Elements (not TraversableElements)
    for link in links:
        assert isinstance(link, Element)
        assert not isinstance(link, TraversableElement)
        assert isinstance(link.attrs["href"], str)

    for script in scripts:
        assert isinstance(script, Element)
        assert not isinstance(script, TraversableElement)
        assert isinstance(script.attrs["src"], str)


def test_make_path_nodes_preserves_other_attrs():
    """Test that transformation preserves all other attributes."""
    tree = html(t"""
        <head>
            <link rel="stylesheet"
                  type="text/css"
                  class="main-styles"
                  href="static/styles.css"
                  media="screen">
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    link = get_by_tag_name(new_tree, "link")
    # Verify href transformed to full module-relative path
    assert isinstance(link.attrs["href"], Traversable)
    assert str(link.attrs["href"]) == "mysite/components/heading/static/styles.css"
    # Verify all other attributes preserved
    assert link.attrs["rel"] == "stylesheet"
    assert link.attrs["type"] == "text/css"
    assert link.attrs["class"] == "main-styles"
    assert link.attrs["media"] == "screen"


# ============================================================================
# @path_nodes Decorator Tests
# ============================================================================


def test_path_nodes_decorator_components():
    """Test @path_nodes decorator on both function and class components."""

    # Function component
    @path_nodes
    def function_component():
        return html(t"""
            <head>
                <link rel="stylesheet" href="static/styles.css">
            </head>
        """)

    # Class component with __call__
    class ClassComponent:
        @path_nodes
        def __call__(self):
            return html(t"""
                <head>
                    <script src="static/script.js"></script>
                </head>
            """)

    # Test function component
    func_result = function_component()
    link = get_by_tag_name(func_result, "link")
    assert isinstance(link, TraversableElement)
    assert isinstance(link.attrs["href"], Traversable)
    # Verify full module-relative path includes test module
    assert "test_tree" in str(link.attrs["href"])
    assert "static/styles.css" in str(link.attrs["href"])

    # Test class component
    component = ClassComponent()
    class_result = component()
    script = get_by_tag_name(class_result, "script")
    assert isinstance(script, TraversableElement)
    assert isinstance(script.attrs["src"], Traversable)
    # Verify full module-relative path includes test module
    assert "test_tree" in str(script.attrs["src"])
    assert "static/script.js" in str(script.attrs["src"])


def test_make_path_nodes_unchanged_nodes():
    """Test that unchanged nodes return the same object (optimization)."""
    tree = html(t"""
        <html>
            <body>
                <div>
                    <p>No assets here</p>
                </div>
            </body>
        </html>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # The tree should be identical since nothing changed
    # (Fragment might be recreated but inner elements should be same)
    body = get_by_tag_name(tree, "body")
    new_body = get_by_tag_name(new_tree, "body")

    # Body element should be the exact same object since it has no assets
    assert body is new_body


# ============================================================================
# Integration Tests (Task Group 4)
# ============================================================================


def test_integration_full_pipeline_make_to_render():
    """Test end-to-end pipeline: make_path_nodes() -> render_path_nodes()."""
    # Step 1: Create HTML with string asset paths
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="static/styles.css">
                <script src="static/app.js"></script>
            </head>
            <body>
                <h1>Welcome</h1>
                <p>Test content</p>
            </body>
        </html>
    """)

    # Step 2: Transform string paths to Traversable (make_path_nodes)
    path_tree = make_path_nodes(tree, Heading)

    # Verify TraversableElement nodes created
    link = get_by_tag_name(path_tree, "link")
    script = get_by_tag_name(path_tree, "script")
    assert isinstance(link, TraversableElement)
    assert isinstance(script, TraversableElement)
    assert isinstance(link.attrs["href"], Traversable)
    assert isinstance(script.attrs["src"], Traversable)

    # Step 3: Render TraversableElement nodes to Element with relative strings (render_path_nodes)
    target = PurePosixPath("mysite/pages/about.html")
    rendered_tree = render_path_nodes(path_tree, target)

    # Verify TraversableElements transformed to regular Elements
    rendered_link = get_by_tag_name(rendered_tree, "link")
    rendered_script = get_by_tag_name(rendered_tree, "script")
    assert isinstance(rendered_link, Element)
    assert not isinstance(rendered_link, TraversableElement)
    assert isinstance(rendered_script, Element)
    assert not isinstance(rendered_script, TraversableElement)

    # Verify relative paths calculated correctly
    assert isinstance(rendered_link.attrs["href"], str)
    assert isinstance(rendered_script.attrs["src"], str)
    assert ".." in rendered_link.attrs["href"]  # Should navigate up from pages/
    assert "components/heading/static/styles.css" in rendered_link.attrs["href"]
    assert ".." in rendered_script.attrs["src"]
    assert "components/heading/static/app.js" in rendered_script.attrs["src"]

    # Verify non-asset content preserved
    h1 = get_by_tag_name(rendered_tree, "h1")
    p = get_by_tag_name(rendered_tree, "p")
    assert isinstance(h1.children[0], Text)
    assert h1.children[0].text == "Welcome"
    assert isinstance(p.children[0], Text)
    assert p.children[0].text == "Test content"


def test_integration_site_prefix_realistic_scenario():
    """Test with site_prefix in realistic multi-page scenario."""
    # Create component tree with assets
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="static/main.css">
                <link rel="stylesheet" href="static/theme.css">
                <script src="static/analytics.js"></script>
            </head>
            <body>
                <nav>Navigation</nav>
                <main>Main content</main>
            </body>
        </html>
    """)

    # Transform to TraversableElements
    path_tree = make_path_nodes(tree, Heading)

    # Render with site_prefix for deployment subdirectory
    strategy = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
    target = PurePosixPath("mysite/pages/docs/guide.html")
    rendered_tree = render_path_nodes(path_tree, target, strategy=strategy)

    # Verify all links use site_prefix
    head = get_by_tag_name(rendered_tree, "head")
    links = get_all_by_tag_name(head, "link")
    scripts = get_all_by_tag_name(head, "script")

    for link in links:
        assert isinstance(link, Element)
        assert not isinstance(link, TraversableElement)
        assert isinstance(link.attrs["href"], str)
        assert link.attrs["href"].startswith("mysite/static")

    for script in scripts:
        assert isinstance(script, Element)
        assert not isinstance(script, TraversableElement)
        assert isinstance(script.attrs["src"], str)
        assert script.attrs["src"].startswith("mysite/static")


def test_integration_multiple_pages_different_targets():
    """Test rendering same tree for multiple pages with different target paths."""
    # Create component tree once
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="static/styles.css">
            </head>
            <body>
                <h1>Shared Component</h1>
            </body>
        </html>
    """)

    path_tree = make_path_nodes(tree, Heading)

    # Render for different target pages
    targets = [
        PurePosixPath("mysite/index.html"),
        PurePosixPath("mysite/pages/about.html"),
        PurePosixPath("mysite/pages/docs/guide.html"),
    ]

    results = []
    for target in targets:
        rendered = render_path_nodes(path_tree, target)
        link = get_by_tag_name(rendered, "link")
        results.append(link.attrs["href"])

    # Verify different relative paths for each target
    assert results[0] == "components/heading/static/styles.css"  # From mysite/
    assert ".." in results[1]  # From mysite/pages/
    assert "components/heading/static/styles.css" in results[1]
    assert "../.." in results[2] or ".." in results[2]  # From mysite/pages/docs/
    assert "components/heading/static/styles.css" in results[2]

    # Verify each result is unique
    assert len(set(results)) == len(results)


def test_integration_preservation_of_non_asset_elements():
    """Test that non-asset elements are preserved through full pipeline."""
    tree = html(t"""
        <html>
            <head>
                <meta charset="utf-8">
                <title>Test Page</title>
                <link rel="stylesheet" href="static/styles.css">
                <meta name="viewport" content="width=device-width">
            </head>
            <body>
                <header>
                    <h1>Header</h1>
                    <nav>
                        <a href="https://example.com">External</a>
                        <a href="#section">Anchor</a>
                    </nav>
                </header>
                <main>
                    <p>Content with <strong>markup</strong></p>
                    <img src="https://example.com/image.jpg" alt="External">
                </main>
                <footer>
                    <!-- Comment preserved -->
                    <p>Footer</p>
                </footer>
            </body>
        </html>
    """)

    # Full pipeline
    path_tree = make_path_nodes(tree, Heading)
    target = PurePosixPath("mysite/pages/index.html")
    rendered_tree = render_path_nodes(path_tree, target)

    # Verify meta tags preserved
    head = get_by_tag_name(rendered_tree, "head")
    metas = get_all_by_tag_name(head, "meta")
    assert len(metas) == 2
    assert metas[0].attrs["charset"] == "utf-8"
    assert metas[1].attrs["name"] == "viewport"

    # Verify title preserved
    title = get_by_tag_name(head, "title")
    assert isinstance(title.children[0], Text)
    assert title.children[0].text == "Test Page"

    # Verify body structure preserved
    body = get_by_tag_name(rendered_tree, "body")
    header = get_by_tag_name(body, "header")
    main = get_by_tag_name(body, "main")
    footer = get_by_tag_name(body, "footer")

    # Verify content preserved
    h1 = get_by_tag_name(header, "h1")
    assert isinstance(h1.children[0], Text)
    assert h1.children[0].text == "Header"

    # Verify external links unchanged
    nav = get_by_tag_name(header, "nav")
    anchors = get_all_by_tag_name(nav, "a")
    assert anchors[0].attrs["href"] == "https://example.com"
    assert anchors[1].attrs["href"] == "#section"

    # Verify markup preserved
    strong = get_by_tag_name(main, "strong")
    assert isinstance(strong.children[0], Text)
    assert strong.children[0].text == "markup"


def test_integration_complex_nested_tree_structures():
    """Test with complex nested tree structures containing TraversableElements."""
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="static/base.css">
            </head>
            <body>
                <div class="outer">
                    <div class="middle">
                        <div class="inner">
                            <section>
                                <article>
                                    <header>
                                        <h1>Nested Content</h1>
                                    </header>
                                    <div class="content">
                                        <p>Text</p>
                                        <div class="widget">
                                            <span>Widget</span>
                                        </div>
                                    </div>
                                </article>
                            </section>
                        </div>
                    </div>
                </div>
                <script src="static/nested.js"></script>
            </body>
        </html>
    """)

    # Full pipeline
    path_tree = make_path_nodes(tree, Heading)
    target = PurePosixPath("mysite/pages/nested/deep/page.html")
    rendered_tree = render_path_nodes(path_tree, target)

    # Verify assets transformed correctly at any depth
    link = get_by_tag_name(rendered_tree, "link")
    script = get_by_tag_name(rendered_tree, "script")
    assert isinstance(link, Element)
    assert isinstance(script, Element)
    assert isinstance(link.attrs["href"], str)
    assert isinstance(script.attrs["src"], str)

    # Verify deep nesting structure preserved
    outer = get_by_tag_name(rendered_tree, "div", attrs={"class": "outer"})
    assert outer.attrs["class"] == "outer"
    middle = get_by_tag_name(outer, "div", attrs={"class": "middle"})
    assert middle.attrs["class"] == "middle"
    inner = get_by_tag_name(middle, "div", attrs={"class": "inner"})
    assert inner.attrs["class"] == "inner"

    # Verify deeply nested content preserved
    widget = None
    for div in get_all_by_tag_name(rendered_tree, "div"):
        if div.attrs.get("class") == "widget":
            widget = div
            break
    assert widget is not None
    span = get_by_tag_name(widget, "span")
    assert isinstance(span.children[0], Text)
    assert span.children[0].text == "Widget"


def test_integration_edge_case_empty_and_text_only_trees():
    """Test edge cases: empty tree and tree with only Text nodes."""
    # Empty tree (just a div with no children)
    empty_tree = Element(tag="div", attrs={}, children=[])
    target = PurePosixPath("mysite/index.html")

    # Should handle empty tree gracefully
    path_tree = make_path_nodes(empty_tree, Heading)
    rendered_tree = render_path_nodes(path_tree, target)
    assert path_tree is empty_tree  # No changes, same object
    assert rendered_tree is path_tree  # No TraversableElements, same object

    # Text-only tree
    text_tree = Element(
        tag="div",
        attrs={},
        children=[
            Text("Hello"),
            Text(" "),
            Text("World"),
        ]
    )

    # Should handle text-only tree gracefully
    path_tree2 = make_path_nodes(text_tree, Heading)
    rendered_tree2 = render_path_nodes(path_tree2, target)
    assert path_tree2 is text_tree  # No changes, same object
    assert rendered_tree2 is path_tree2  # No TraversableElements, same object

    # Verify text content preserved
    assert isinstance(rendered_tree2.children[0], Text)
    assert rendered_tree2.children[0].text == "Hello"
    assert isinstance(rendered_tree2.children[1], Text)
    assert rendered_tree2.children[1].text == " "
    assert isinstance(rendered_tree2.children[2], Text)
    assert rendered_tree2.children[2].text == "World"

    # Fragment with only Text and Comment nodes
    fragment_tree = Fragment(children=[
        Text("Start"),
        Comment("Comment here"),
        Text("End"),
    ])

    path_tree3 = make_path_nodes(fragment_tree, Heading)
    rendered_tree3 = render_path_nodes(path_tree3, target)
    assert path_tree3 is fragment_tree  # No changes
    assert rendered_tree3 is path_tree3  # No TraversableElements


# ============================================================================
# Asset Validation Tests (Task Group 3)
# ============================================================================


def test_validate_asset_exists_with_existing_asset():
    """Test _validate_asset_exists passes for existing assets."""
    from tdom_path.tree import _validate_asset_exists

    # Test with existing asset from fake_package
    asset_path = make_path(None, "tests.fixtures.fake_package:static/styles.css")
    component = Heading
    attr_name = "href"

    # Should not raise any exception
    _validate_asset_exists(asset_path, component, attr_name)


def test_validate_asset_exists_with_missing_asset():
    """Test _validate_asset_exists fails for missing assets."""
    import pytest
    from tdom_path.tree import _validate_asset_exists

    # Test with non-existent asset from fake_package
    asset_path = make_path(None, "tests.fixtures.fake_package:static/nonexistent.css")
    component = Heading
    attr_name = "href"

    # Should raise FileNotFoundError with clear message
    with pytest.raises(FileNotFoundError) as exc_info:
        _validate_asset_exists(asset_path, component, attr_name)

    # Error message should include asset path and context
    error_msg = str(exc_info.value)
    assert "nonexistent.css" in error_msg
    assert attr_name in error_msg


def test_validate_asset_exists_error_message_includes_component():
    """Test validation error messages include component context."""
    import pytest
    from tdom_path.tree import _validate_asset_exists

    # Test with missing asset
    asset_path = make_path(None, "tests.fixtures.fake_package:static/missing.js")
    component = Heading
    attr_name = "src"

    # Should raise with component information
    with pytest.raises(FileNotFoundError) as exc_info:
        _validate_asset_exists(asset_path, component, attr_name)

    error_msg = str(exc_info.value)
    assert "Heading" in error_msg or "mysite.components.heading" in error_msg


def test_make_path_nodes_validates_assets():
    """Test that make_path_nodes validates asset existence during transformation."""
    import pytest

    # Create tree with non-existent asset
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="tests.fixtures.fake_package:static/missing.css">
            </head>
        </html>
    """)

    # Should raise FileNotFoundError during transformation
    with pytest.raises(FileNotFoundError) as exc_info:
        make_path_nodes(tree, Heading)

    # Error should mention the missing asset
    error_msg = str(exc_info.value)
    assert "missing.css" in error_msg


def test_make_path_nodes_validates_multiple_assets():
    """Test validation runs for all assets in tree."""
    import pytest

    # Create tree with one valid and one invalid asset
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="tests.fixtures.fake_package:static/styles.css">
                <script src="tests.fixtures.fake_package:static/nonexistent.js"></script>
            </head>
        </html>
    """)

    # Should fail on the first missing asset
    with pytest.raises(FileNotFoundError) as exc_info:
        make_path_nodes(tree, Heading)

    error_msg = str(exc_info.value)
    assert "nonexistent.js" in error_msg


def test_make_path_nodes_skips_validation_for_external_urls():
    """Test that validation is not performed on external URLs."""
    # Create tree with external URL (should not validate)
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="https://cdn.example.com/nonexistent.css">
            </head>
        </html>
    """)

    # Should not raise any exception (external URLs are not validated)
    result = make_path_nodes(tree, Heading)

    # External URL should remain unchanged
    link = get_by_tag_name(result, "link")
    assert link.attrs["href"] == "https://cdn.example.com/nonexistent.css"


def test_validate_asset_exists_with_package_paths():
    """Test validation works correctly with package paths."""
    from tdom_path.tree import _validate_asset_exists

    # Test with valid package path
    asset_path = make_path(None, "tests.fixtures.fake_package:images/logo.png")

    # Should not raise any exception
    _validate_asset_exists(asset_path, Heading, "src")


def test_validate_asset_exists_error_includes_path_string():
    """Test error messages include the full asset path for debugging."""
    import pytest
    from tdom_path.tree import _validate_asset_exists

    # Test with missing asset
    asset_path = make_path(None, "tests.fixtures.fake_package:static/notfound.css")

    # Should include path information in error
    with pytest.raises(FileNotFoundError) as exc_info:
        _validate_asset_exists(asset_path, Heading, "href")

    error_msg = str(exc_info.value)
    # Should include the asset path or filename
    assert "notfound.css" in error_msg or str(asset_path) in error_msg


# ============================================================================
# Traversable Type Compatibility Tests (Task Group 4)
# ============================================================================


def test_traversable_element_accepts_traversable_attributes():
    """Test TraversableElement accepts Traversable attribute values (not just PurePosixPath)."""
    from importlib.resources.abc import Traversable

    # Get a Traversable instance from make_path
    traversable = make_path(Heading, "static/styles.css")

    # Verify it's a Traversable (not just PurePosixPath)
    assert isinstance(traversable, Traversable)

    # TraversableElement should accept Traversable values
    elem = TraversableElement(
        tag="link",
        attrs={"rel": "stylesheet", "href": traversable},
        children=[]
    )

    assert elem.attrs["href"] is traversable
    assert isinstance(elem.attrs["href"], Traversable)


def test_transform_asset_element_returns_traversable_attributes():
    """Test _transform_asset_element creates TraversableElement with Traversable values."""
    from importlib.resources.abc import Traversable
    from tdom_path.tree import _transform_asset_element

    elem = Element(
        tag="link",
        attrs={"rel": "stylesheet", "href": "static/styles.css"},
        children=[]
    )

    result = _transform_asset_element(elem, "href", Heading)

    # Should return TraversableElement with Traversable href
    assert isinstance(result, TraversableElement)
    assert isinstance(result.attrs["href"], Traversable)
    assert str(result.attrs["href"]) == "mysite/components/heading/static/styles.css"


def test_render_transform_node_handles_traversable_values():
    """Test _render_transform_node converts Traversable attributes to strings."""
    from importlib.resources.abc import Traversable
    from tdom_path.tree import _render_transform_node

    traversable = make_path(Heading, "static/styles.css")
    assert isinstance(traversable, Traversable)

    strategy = RelativePathStrategy()
    target = PurePosixPath("mysite/components/heading/index.html")

    node = TraversableElement(
        tag="link",
        attrs={"rel": "stylesheet", "href": traversable},
        children=[]
    )

    result = _render_transform_node(node, target, strategy)

    # Should convert Traversable to string
    assert isinstance(result, Element)
    assert not isinstance(result, TraversableElement)
    assert isinstance(result.attrs["href"], str)
    assert result.attrs["href"] == "static/styles.css"


def test_render_path_nodes_with_traversable_attributes():
    """Test render_path_nodes() handles Traversable attributes throughout the tree."""
    from importlib.resources.abc import Traversable

    # Create tree with Traversable attributes
    css_path = make_path(Heading, "static/styles.css")
    js_path = make_path(Heading, "static/app.js")

    assert isinstance(css_path, Traversable)
    assert isinstance(js_path, Traversable)

    tree = Element(
        tag="html",
        attrs={},
        children=[
            Element(
                tag="head",
                attrs={},
                children=[
                    TraversableElement(
                        tag="link",
                        attrs={"rel": "stylesheet", "href": css_path},
                        children=[]
                    ),
                    TraversableElement(
                        tag="script",
                        attrs={"src": js_path},
                        children=[]
                    )
                ]
            )
        ]
    )

    target = PurePosixPath("mysite/pages/index.html")
    result = render_path_nodes(tree, target)

    # Verify Traversable attributes converted to strings
    head = get_by_tag_name(result, "head")
    link = get_by_tag_name(head, "link")
    script = get_by_tag_name(head, "script")

    assert isinstance(link.attrs["href"], str)
    assert isinstance(script.attrs["src"], str)
    assert ".." in link.attrs["href"]
    assert "components/heading/static/styles.css" in link.attrs["href"]


def test_relative_path_strategy_accepts_traversable_source():
    """Test RelativePathStrategy.calculate_path() works with Traversable source."""
    from importlib.resources.abc import Traversable

    strategy = RelativePathStrategy()

    # Get Traversable instance
    source = make_path(Heading, "static/styles.css")
    assert isinstance(source, Traversable)

    target = PurePosixPath("mysite/components/heading/index.html")

    # Should accept Traversable as source parameter
    result = strategy.calculate_path(source, target)

    assert isinstance(result, str)
    assert result == "static/styles.css"


def test_package_path_returns_traversable():
    """Test package paths return Traversable instances (not PurePosixPath)."""
    from importlib.resources.abc import Traversable

    # Package path syntax
    pkg_path = make_path(None, "tests.fixtures.fake_package:static/styles.css")

    # Should return Traversable
    assert isinstance(pkg_path, Traversable)
    # Should be file-like
    assert pkg_path.is_file()


def test_mixed_traversable_and_string_attributes():
    """Test TraversableElement can have mixed Traversable and string attributes."""
    from importlib.resources.abc import Traversable

    traversable = make_path(Heading, "static/styles.css")
    assert isinstance(traversable, Traversable)

    elem = TraversableElement(
        tag="link",
        attrs={
            "rel": "stylesheet",
            "href": traversable,
            "type": "text/css",
            "media": None
        },
        children=[]
    )

    # Should support mixed types
    assert isinstance(elem.attrs["href"], Traversable)
    assert isinstance(elem.attrs["rel"], str)
    assert isinstance(elem.attrs["type"], str)
    assert elem.attrs["media"] is None


def test_end_to_end_package_path_with_traversable():
    """Test end-to-end: package path -> Traversable -> rendered string."""
    from importlib.resources.abc import Traversable

    # Create tree with package path
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="tests.fixtures.fake_package:static/styles.css">
            </head>
        </html>
    """)

    # Transform to Traversable
    path_tree = make_path_nodes(tree, Heading)
    link = get_by_tag_name(path_tree, "link")

    # Should have Traversable attribute
    assert isinstance(link, TraversableElement)
    assert isinstance(link.attrs["href"], Traversable)

    # Render to string
    target = PurePosixPath("mysite/pages/index.html")
    rendered_tree = render_path_nodes(path_tree, target)

    rendered_link = get_by_tag_name(rendered_tree, "link")

    # Should convert to string
    assert isinstance(rendered_link, Element)
    assert not isinstance(rendered_link, TraversableElement)
    assert isinstance(rendered_link.attrs["href"], str)

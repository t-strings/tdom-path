"""Tests for make_path_nodes tree rewriting functionality.

These tests use HTML template strings for more readable test cases.
Focus on core functionality:
- Tree walking and element transformation
- Detection of <link> and <script> tags
- Skipping external URLs and special schemes
- Decorator support for function and class components
"""

from importlib.resources.abc import Traversable

from tdom import Element, Text, html
from mysite.components.heading import Heading
from tdom_path import make_path_nodes, path_nodes
from tdom_path.tree import TraversableElement
from tdom_path.webpath import make_path


def _find_elements(node):
    """Helper to find Element children, skipping Text nodes."""
    return [child for child in node.children if isinstance(child, Element)]


def _find_element_by_tag(node, tag):
    """Recursively find first element with given tag."""
    if isinstance(node, Element) and node.tag == tag:
        return node
    if hasattr(node, "children"):
        for child in node.children:
            result = _find_element_by_tag(child, tag)
            if result:
                return result
    return None


# ============================================================================
# TraversableElement Class Tests (Task Group 1)
# ============================================================================


def test_traversable_element_instantiation_and_attrs():
    """Test TraversableElement instantiation with mixed attr types."""
    import pytest

    traversable_path = make_path(Heading, "static/styles.css")

    # Test with mixed attr types (str, Traversable, None)
    elem = TraversableElement(
        tag="link",
        attrs={
            "rel": "stylesheet",
            "href": traversable_path,
            "type": "text/css",
            "media": None
        },
        children=[]
    )

    assert elem.tag == "link"
    assert isinstance(elem.attrs["href"], Traversable)
    assert isinstance(elem.attrs["rel"], str)
    assert isinstance(elem.attrs["type"], str)
    assert elem.attrs["media"] is None
    assert "static/styles.css" in str(elem.attrs["href"])

    # Test inherited validation from Element
    with pytest.raises(ValueError, match="Element tag cannot be empty"):
        TraversableElement(tag="", attrs={}, children=[])


def test_traversable_element_inheritance():
    """Test TraversableElement properly inherits Element behavior."""
    traversable_path = make_path(Heading, "static/styles.css")

    elem = TraversableElement(
        tag="link",
        attrs={"href": traversable_path},
        children=[]
    )

    # Verify it's an Element subclass
    assert isinstance(elem, Element)

    # Verify dataclass(slots=True) configuration
    assert not hasattr(elem, "__dict__")
    assert hasattr(elem, "tag")
    assert hasattr(elem, "attrs")
    assert hasattr(elem, "children")

    # Verify immutability pattern (creating new instances)
    new_elem = TraversableElement(
        tag="script",
        attrs=elem.attrs,
        children=elem.children
    )
    assert new_elem.tag == "script"
    assert elem.tag == "link"  # Original unchanged


def test_traversable_element_rendering():
    """Test TraversableElement HTML rendering with Traversable auto-conversion."""
    traversable_path = make_path(Heading, "static/script.js")

    # Test rendering with Traversable attr and children
    elem = TraversableElement(
        tag="script",
        attrs={"src": traversable_path},
        children=[Text("// comment")]
    )

    html_str = str(elem)
    assert html_str.startswith("<script")
    assert "static/script.js" in html_str
    assert "// comment" in html_str
    assert html_str.endswith("</script>")

    # Test rendering with string attrs (no Traversable)
    elem2 = TraversableElement(
        tag="div",
        attrs={"class": "container"},
        children=[]
    )
    assert str(elem2) == '<div class="container"></div>'


# ============================================================================
# Tree Walker Integration Tests (Task Group 2)
# ============================================================================


def test_tree_walker_creates_traversable_element_for_link_with_traversable():
    """Test that link element with Traversable href creates TraversableElement."""
    tree = html(t"""
        <head>
            <link rel="stylesheet" href="static/styles.css">
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # Find the link element
    link = _find_element_by_tag(new_tree, "link")

    # Verify it's a TraversableElement (not just Element)
    assert isinstance(link, TraversableElement)
    assert isinstance(link.attrs["href"], Traversable)
    assert "static/styles.css" in str(link.attrs["href"])


def test_tree_walker_creates_traversable_element_for_script_with_traversable():
    """Test that script element with Traversable src creates TraversableElement."""
    tree = html(t"""
        <head>
            <script src="static/script.js"></script>
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    script = _find_element_by_tag(new_tree, "script")

    # Verify it's a TraversableElement
    assert isinstance(script, TraversableElement)
    assert isinstance(script.attrs["src"], Traversable)
    assert "static/script.js" in str(script.attrs["src"])


def test_tree_walker_creates_element_for_link_with_string():
    """Test that link element with string href creates Element (not TraversableElement)."""
    tree = html(t"""
        <head>
            <link rel="stylesheet" href="https://cdn.example.com/style.css">
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    link = _find_element_by_tag(new_tree, "link")

    # Should be regular Element since external URL wasn't transformed
    assert isinstance(link, Element)
    assert not isinstance(link, TraversableElement)
    assert isinstance(link.attrs["href"], str)
    assert link.attrs["href"] == "https://cdn.example.com/style.css"


def test_tree_walker_mixed_tree_element_and_traversable_element():
    """Test mixed tree with both Element and TraversableElement types."""
    tree = html(t"""
        <head>
            <link rel="stylesheet" href="https://cdn.example.com/external.css">
            <link rel="stylesheet" href="static/local.css">
            <script src="static/script.js"></script>
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    head = _find_element_by_tag(new_tree, "head")
    links = [child for child in head.children if isinstance(child, Element) and child.tag == "link"]
    script = _find_element_by_tag(new_tree, "script")

    # External link should be regular Element
    external_link = links[0]
    assert isinstance(external_link, Element)
    assert not isinstance(external_link, TraversableElement)
    assert isinstance(external_link.attrs["href"], str)

    # Local link should be TraversableElement
    local_link = links[1]
    assert isinstance(local_link, TraversableElement)
    assert isinstance(local_link.attrs["href"], Traversable)

    # Script should be TraversableElement
    assert isinstance(script, TraversableElement)
    assert isinstance(script.attrs["src"], Traversable)


def test_tree_walker_preserves_traversable_element_type_through_walking():
    """Test TraversableElement type preserved through tree walking."""
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="static/styles.css">
            </head>
            <body>
                <div>
                    <script src="static/script.js"></script>
                </div>
            </body>
        </html>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # Find elements at different depths
    link = _find_element_by_tag(new_tree, "link")
    script = _find_element_by_tag(new_tree, "script")

    # Both should be TraversableElement
    assert isinstance(link, TraversableElement)
    assert isinstance(script, TraversableElement)

    # Parent elements should still be regular Element
    head = _find_element_by_tag(new_tree, "head")
    body = _find_element_by_tag(new_tree, "body")
    assert isinstance(head, Element)
    assert not isinstance(head, TraversableElement)
    assert isinstance(body, Element)
    assert not isinstance(body, TraversableElement)


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

    # Verify TraversableElement instances created
    link = _find_element_by_tag(new_tree, "link")
    script = _find_element_by_tag(new_tree, "script")
    assert isinstance(link, TraversableElement)
    assert isinstance(script, TraversableElement)

    # Verify rendering with Traversable auto-conversion
    html_output = str(new_tree)
    assert "static/styles.css" in html_output
    assert "static/app.js" in html_output
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
    link = _find_element_by_tag(result, "link")

    assert isinstance(link, TraversableElement)
    assert isinstance(link.attrs["href"], Traversable)


def test_integration_not_exported_from_main_module():
    """Test that TraversableElement is NOT exposed in public API."""
    import tdom_path

    assert "TraversableElement" not in tdom_path.__all__
    assert not hasattr(tdom_path, "TraversableElement")

    # Verify it's only accessible from tree module
    from tdom_path.tree import TraversableElement as TreeTraversableElement
    assert TreeTraversableElement is not None


# ============================================================================
# Original Tree Rewriting Tests
# ============================================================================


def test_make_path_nodes_link_element():
    """Test transformation of <link> tag with href."""
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="static/styles.css">
            </head>
        </html>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # Find the link element
    link = _find_element_by_tag(new_tree, "link")

    # Verify href is now Traversable
    assert isinstance(link.attrs["href"], Traversable)
    assert "static/styles.css" in str(link.attrs["href"])
    assert link.attrs["rel"] == "stylesheet"


def test_make_path_nodes_script_tag():
    """Test transformation of <script> tag with src."""
    tree = html(t"""
        <html>
            <head>
                <script src="static/script.js"></script>
            </head>
        </html>
    """)

    new_tree = make_path_nodes(tree, Heading)

    script = _find_element_by_tag(new_tree, "script")

    assert isinstance(script.attrs["src"], Traversable)
    assert "static/script.js" in str(script.attrs["src"])


def test_make_path_nodes_external_urls():
    """Test that external URLs are not transformed."""
    tree = html(t"""
        <head>
            <link rel="stylesheet" href="http://cdn.example.com/style.css">
            <link rel="stylesheet" href="https://cdn.example.com/style.css">
            <link rel="stylesheet" href="//cdn.example.com/style.css">
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # Verify all hrefs remain as strings
    head = _find_element_by_tag(new_tree, "head")
    links = _find_elements(head)
    for link in links:
        assert isinstance(link.attrs["href"], str)
        assert "cdn.example.com" in link.attrs["href"]


def test_make_path_nodes_special_schemes():
    """Test that special schemes are not transformed."""
    tree = html(t"""
        <head>
            <link rel="me" href="mailto:user@example.com">
            <link rel="me" href="tel:+1234567890">
            <link rel="icon" href="data:image/png;base64,abc123">
            <script src="javascript:void(0)"></script>
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # Verify all remain as strings
    head = _find_element_by_tag(new_tree, "head")
    elements = _find_elements(head)
    for elem in elements:
        href_or_src = elem.attrs.get("href") or elem.attrs.get("src")
        assert isinstance(href_or_src, str)


def test_make_path_nodes_anchor_only():
    """Test that anchor-only links are not transformed."""
    tree = html(t"""
        <head>
            <link rel="canonical" href="#section">
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    link = _find_element_by_tag(new_tree, "link")
    assert isinstance(link.attrs["href"], str)
    assert link.attrs["href"] == "#section"


def test_make_path_nodes_mixed_assets():
    """Test tree with both external and local assets."""
    tree = html(t"""
        <head>
            <link rel="stylesheet" href="https://cdn.example.com/style.css">
            <link rel="stylesheet" href="static/styles.css">
        </head>
    """)

    new_tree = make_path_nodes(tree, Heading)

    head = _find_element_by_tag(new_tree, "head")
    links = _find_elements(head)

    # External remains string
    external_link = links[0]
    assert isinstance(external_link.attrs["href"], str)
    assert "cdn.example.com" in external_link.attrs["href"]

    # Local becomes Traversable
    local_link = links[1]
    assert isinstance(local_link.attrs["href"], Traversable)
    assert "static/styles.css" in str(local_link.attrs["href"])


def test_make_path_nodes_nested_children():
    """Test deep tree traversal with nested children."""
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="static/styles.css">
            </head>
            <body>
                <div>
                    <script src="static/script.js"></script>
                </div>
            </body>
        </html>
    """)

    new_tree = make_path_nodes(tree, Heading)

    # Find link in head
    link = _find_element_by_tag(new_tree, "link")
    assert isinstance(link.attrs["href"], Traversable)

    # Find script in body > div
    script = _find_element_by_tag(new_tree, "script")
    assert isinstance(script.attrs["src"], Traversable)


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

    link = _find_element_by_tag(new_tree, "link")
    assert isinstance(link.attrs["href"], Traversable)
    assert link.attrs["rel"] == "stylesheet"
    assert link.attrs["type"] == "text/css"
    assert link.attrs["class"] == "main-styles"
    assert link.attrs["media"] == "screen"


def test_path_nodes_decorator_class_component():
    """Test @path_nodes decorator on class component __call__ method."""

    class TestComponent:
        @path_nodes
        def __call__(self):
            return html(t"""
                <head>
                    <link rel="stylesheet" href="static/styles.css">
                </head>
            """)

    component = TestComponent()
    result = component()

    link = _find_element_by_tag(result, "link")
    assert isinstance(link.attrs["href"], Traversable)
    assert "static/styles.css" in str(link.attrs["href"])


def test_path_nodes_decorator_function_component():
    """Test @path_nodes decorator on function component."""

    @path_nodes
    def test_component():
        return html(t"""
            <head>
                <link rel="stylesheet" href="static/styles.css">
            </head>
        """)

    result = test_component()

    link = _find_element_by_tag(result, "link")
    assert isinstance(link.attrs["href"], Traversable)
    assert "static/styles.css" in str(link.attrs["href"])


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
    body = _find_element_by_tag(tree, "body")
    new_body = _find_element_by_tag(new_tree, "body")

    # Body element should be the exact same object since it has no assets
    assert body is new_body

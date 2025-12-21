"""Tests for make_path_nodes tree rewriting functionality.

These tests use HTML template strings for more readable test cases.
Focus on core functionality:
- Tree walking and element transformation
- Detection of <link> and <script> tags
- Skipping external URLs and special schemes
- Decorator support for function and class components
"""

from importlib.resources.abc import Traversable

from tdom import Element, html
from mysite.components.heading import Heading
from tdom_path import make_path_nodes, path_nodes


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

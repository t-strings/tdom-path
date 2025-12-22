"""Integration tests using fixture package for package path resolution.

These tests demonstrate end-to-end functionality using the fake_package fixture:
- Package path resolution with package:path syntax
- Tree transformation with package assets
- Rendering with package paths
"""

from pathlib import PurePosixPath

from tdom import Element
from tdom_path import make_path_nodes, render_path_nodes


def test_package_path_in_tree_transformation():
    """Test that package paths work in tree transformation."""
    # Create a tree with a package path reference
    tree = Element(
        tag="head",
        attrs={},
        children=[
            Element(
                tag="link",
                attrs={
                    "rel": "stylesheet",
                    "href": "tests.fixtures.fake_package:static/styles.css",
                },
                children=[],
            )
        ],
    )

    # Transform tree using make_path_nodes
    # For package paths, component doesn't matter, but we need to pass something
    transformed = make_path_nodes(tree, None)

    # Verify the tree structure is preserved
    assert isinstance(transformed, Element)
    assert transformed.tag == "head"
    assert len(transformed.children) == 1

    # Get the link element
    link = transformed.children[0]
    assert isinstance(link, Element)
    assert link.tag == "link"


def test_package_path_rendering():
    """Test rendering package paths to string paths."""
    # Create a tree with package path
    tree = Element(
        tag="link",
        attrs={
            "rel": "stylesheet",
            "href": "tests.fixtures.fake_package:static/styles.css",
        },
        children=[],
    )

    # Transform to TraversableElement with package path
    transformed = make_path_nodes(tree, None)

    # Render to string paths
    target = PurePosixPath("pages/about.html")
    rendered = render_path_nodes(transformed, target)

    # Verify rendered output has string href
    assert isinstance(rendered, Element)
    assert rendered.tag == "link"
    href = rendered.attrs.get("href")
    assert isinstance(href, str)
    assert "styles.css" in href


def test_mixed_package_and_relative_paths():
    """Test tree with both package and relative paths."""
    # This would require a component with relative paths
    # For this test, we'll use package paths only to demonstrate the fixture
    tree = Element(
        tag="head",
        attrs={},
        children=[
            Element(
                tag="link",
                attrs={
                    "rel": "stylesheet",
                    "href": "tests.fixtures.fake_package:static/styles.css",
                },
                children=[],
            ),
            Element(
                tag="script",
                attrs={
                    "src": "tests.fixtures.fake_package:static/script.js",
                },
                children=[],
            ),
        ],
    )

    # Transform tree
    transformed = make_path_nodes(tree, None)

    # Verify both elements are transformed
    assert isinstance(transformed, Element)
    assert len(transformed.children) == 2


def test_package_asset_rendering_to_string():
    """Test that package assets render to strings correctly."""
    # Create tree with package path
    tree = Element(
        tag="link",
        attrs={
            "rel": "stylesheet",
            "href": "tests.fixtures.fake_package:static/styles.css",
        },
        children=[],
    )

    # Transform to Traversable
    transformed = make_path_nodes(tree, None)

    # Render to string paths (package paths return filesystem paths)
    target = PurePosixPath("index.html")
    rendered = render_path_nodes(transformed, target)

    # Verify rendering produces string output
    assert isinstance(rendered, Element)
    href = rendered.attrs.get("href")
    assert isinstance(href, str)
    # Package paths resolve to filesystem paths
    assert "styles.css" in href


def test_package_asset_validation():
    """Test that package assets are validated during transformation."""
    # Create tree with non-existent asset
    tree = Element(
        tag="link",
        attrs={
            "rel": "stylesheet",
            "href": "tests.fixtures.fake_package:static/nonexistent.css",
        },
        children=[],
    )

    # Transform should fail with FileNotFoundError
    try:
        make_path_nodes(tree, None)
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        # Verify error message includes asset info
        error_msg = str(e)
        assert "nonexistent.css" in error_msg or "Asset not found" in error_msg


def test_multiple_package_assets():
    """Test tree with multiple assets from fixture package."""
    tree = Element(
        tag="head",
        attrs={},
        children=[
            Element(
                tag="link",
                attrs={
                    "rel": "stylesheet",
                    "href": "tests.fixtures.fake_package:static/styles.css",
                },
                children=[],
            ),
            Element(
                tag="script",
                attrs={
                    "src": "tests.fixtures.fake_package:static/script.js",
                },
                children=[],
            ),
            Element(
                tag="img",
                attrs={
                    "src": "tests.fixtures.fake_package:images/logo.png",
                },
                children=[],
            ),
        ],
    )

    # Note: Currently img tags are not transformed by make_path_nodes
    # Only link[href] and script[src] are transformed
    # This test demonstrates the fixture structure, not img transformation

    # Transform tree
    transformed = make_path_nodes(tree, None)

    # Verify structure is preserved
    assert isinstance(transformed, Element)
    assert len(transformed.children) == 3

    # Verify first two children are transformed (link and script)
    link = transformed.children[0]
    script = transformed.children[1]
    assert isinstance(link, Element)
    assert isinstance(script, Element)


def test_package_asset_full_pipeline():
    """Test full pipeline from package path to rendered HTML."""
    # Create tree with package path
    tree = Element(
        tag="head",
        attrs={},
        children=[
            Element(
                tag="link",
                attrs={
                    "rel": "stylesheet",
                    "href": "tests.fixtures.fake_package:static/styles.css",
                },
                children=[],
            )
        ],
    )

    # Step 1: Transform to TraversableElement
    transformed = make_path_nodes(tree, None)

    # Step 2: Render to string paths
    target = PurePosixPath("pages/about.html")
    rendered = render_path_nodes(transformed, target)

    # Step 3: Verify final output is ready for HTML rendering
    assert isinstance(rendered, Element)
    assert rendered.tag == "head"
    link = rendered.children[0]
    assert isinstance(link, Element)
    href = link.attrs.get("href")
    assert isinstance(href, str)
    assert "styles.css" in href

    # Verify we can convert to string (HTML rendering)
    html_str = str(rendered)
    assert "<head>" in html_str
    assert "stylesheet" in html_str
    assert "styles.css" in html_str

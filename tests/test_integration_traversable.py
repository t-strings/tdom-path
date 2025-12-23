"""Integration tests for package path support.

Focuses on package path-specific functionality (package:path syntax).
General integration tests are in test_tree.py.
"""

import pytest
from pathlib import PurePosixPath
from importlib.resources.abc import Traversable

from tdom import html, Element
from mysite.components.heading import Heading
from tdom_path import make_path, make_path_nodes, render_path_nodes
from tdom_path.tree import TraversableElement, _TraversableWithPath
from aria_testing import get_by_tag_name


# Helper to check if value is traversable or wrapped traversable
def _is_traversable_or_wrapped(value) -> bool:
    """Check if value is a Traversable or _TraversableWithPath."""
    return isinstance(value, (Traversable, _TraversableWithPath))


def test_package_path_syntax():
    """Test that package:path syntax resolves correctly."""
    tree = html(t"""
        <link rel="stylesheet" href="tests.fixtures.fake_package:static/styles.css">
    """)

    path_tree = make_path_nodes(tree, Heading)
    link = get_by_tag_name(path_tree, "link")

    assert isinstance(link, TraversableElement)
    assert _is_traversable_or_wrapped(link.attrs["href"])


def test_package_path_multiple_assets():
    """Test tree with multiple package path assets."""
    tree = html(t"""
        <html>
            <head>
                <link rel="stylesheet" href="tests.fixtures.fake_package:static/styles.css">
                <script src="tests.fixtures.fake_package:static/script.js"></script>
            </head>
        </html>
    """)

    path_tree = make_path_nodes(tree, Heading)
    link = get_by_tag_name(path_tree, "link")
    script = get_by_tag_name(path_tree, "script")

    assert isinstance(link, TraversableElement)
    assert isinstance(script, TraversableElement)
    assert _is_traversable_or_wrapped(link.attrs["href"])
    assert _is_traversable_or_wrapped(script.attrs["src"])


def test_package_path_error_missing_package():
    """Test error when package doesn't exist."""
    tree = html(t"""
        <link href="nonexistent_package_xyz:static/styles.css">
    """)

    with pytest.raises((ModuleNotFoundError, ImportError)) as exc_info:
        make_path_nodes(tree, Heading)

    assert "nonexistent_package_xyz" in str(exc_info.value) or "No module named" in str(
        exc_info.value
    )


def test_package_path_error_missing_asset():
    """Test error when asset doesn't exist in package."""
    tree = html(t"""
        <link href="tests.fixtures.fake_package:static/nonexistent.css">
    """)

    with pytest.raises(FileNotFoundError) as exc_info:
        make_path_nodes(tree, Heading)

    assert "nonexistent.css" in str(exc_info.value)


def test_package_path_renders_to_string():
    """Test that package paths render to strings."""
    tree = html(t"""
        <link href="tests.fixtures.fake_package:static/styles.css">
    """)

    path_tree = make_path_nodes(tree, Heading)
    target = PurePosixPath("mysite/pages/index.html")
    rendered_tree = render_path_nodes(path_tree, target)

    link = get_by_tag_name(rendered_tree, "link")
    assert isinstance(link, Element)
    assert not isinstance(link, TraversableElement)
    assert isinstance(link.attrs["href"], str)
    assert len(link.attrs["href"]) > 0

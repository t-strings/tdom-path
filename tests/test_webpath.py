"""Tests for make_path function with importlib.resources integration.

These tests focus on make_path functionality:
- Resolving component package locations using importlib.resources
- Creating paths to static assets (CSS, JS, images)
- Working with actual package resources
- Filesystem operations on returned paths
"""

from importlib.resources.abc import Traversable

from mysite.components.heading import Heading
from tdom_path import make_path


def test_make_path_basic():
    """Test basic make_path functionality with component and asset."""
    # Create path to static CSS file
    css_path = make_path(Heading, "static/styles.css")

    # Should return a Traversable (path-like object)
    assert isinstance(css_path, Traversable)

    # Path should contain the component package structure and asset
    path_str = str(css_path)
    assert "mysite/components/heading/static/styles.css" in path_str


def test_make_path_file_exists():
    """Test that make_path resolves to actual existing file with filesystem operations."""
    # Create path to the CSS file
    css_path = make_path(Heading, "static/styles.css")

    # Verify the path points to an actual file
    # Note: In development, this uses the examples directory
    # In production (wheel), it would use installed package location
    assert "styles.css" in str(css_path)

    # Test filesystem operations
    assert css_path.is_file()
    assert not css_path.is_dir()

    # Can read the file content
    content = css_path.read_text()
    assert "h1" in content


def test_make_path_component_instance():
    """Test make_path works with component instance."""
    # Create component instance
    heading = Heading("Test Heading")

    # make_path should work with instance (extracts __module__ from class)
    css_path = make_path(heading, "static/styles.css")

    assert isinstance(css_path, Traversable)
    assert "static/styles.css" in str(css_path)


def test_make_path_different_assets():
    """Test make_path with different asset paths."""
    # CSS file
    css_path = make_path(Heading, "static/styles.css")
    assert "styles.css" in str(css_path)

    # JavaScript file
    js_path = make_path(Heading, "static/script.js")
    assert "script.js" in str(js_path)

    # Image file in subdirectory
    img_path = make_path(Heading, "static/images/logo.png")
    assert "images/logo.png" in str(img_path)


def test_make_path_no_module_attribute():
    """Test that make_path raises TypeError for objects without __module__."""
    # Plain string has no __module__
    try:
        make_path("not_a_component", "static/styles.css")
        assert False, "Should have raised TypeError"
    except TypeError as e:
        assert "__module__" in str(e)

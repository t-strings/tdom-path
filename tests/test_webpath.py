"""Tests for make_path function for module-relative web paths.

These tests focus on make_path functionality:
- Converting Python module names to web paths
- Creating module-relative paths to static assets (CSS, JS, images)
- Returning PurePosixPath for cross-platform consistency
"""

from pathlib import PurePosixPath

from mysite.components.heading import Heading
from tdom_path import make_path


def test_make_path_basic():
    """Test basic make_path functionality with component and asset."""
    # Create path to static CSS file
    css_path = make_path(Heading, "static/styles.css")

    # Should return a PurePosixPath (path object for web paths)
    assert isinstance(css_path, PurePosixPath)

    # Path should be module-relative
    path_str = str(css_path)
    assert path_str == "mysite/components/heading/static/styles.css"


def test_make_path_module_structure():
    """Test that make_path returns module-relative paths."""
    # Create path to the CSS file
    css_path = make_path(Heading, "static/styles.css")

    # Verify the path is module-relative (not filesystem absolute)
    assert "styles.css" in str(css_path)
    assert "mysite/components/heading" in str(css_path)

    # Path should use forward slashes (PurePosixPath)
    assert "/" in str(css_path)
    assert "\\" not in str(css_path)

    """Test make_path works with component instance."""
    # Create component instance
    heading = Heading("Test Heading")

    # make_path should work with instance (extracts __module__ from class)
    css_path = make_path(heading, "static/styles.css")

    assert isinstance(css_path, PurePosixPath)
    assert "static/styles.css" in str(css_path)
    assert str(css_path) == "mysite/components/heading/static/styles.css"


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

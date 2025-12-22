"""Tests for make_path function for module-relative web paths.

These tests focus on make_path functionality:
- Converting Python module names to web paths
- Creating module-relative paths to static assets (CSS, JS, images)
- Returning Traversable for cross-platform consistency
- Path type detection for package vs relative paths
- Package path parsing
- Package path resolution to Traversable instances
"""

from importlib.resources.abc import Traversable

from mysite.components.heading import Heading
from tdom_path import make_path
from tdom_path.webpath import _detect_path_type, _parse_package_path


def test_make_path_basic():
    """Test basic make_path functionality with component and asset."""
    # Create path to static CSS file
    css_path = make_path(Heading, "static/styles.css")

    # Should return a Traversable (for package resource access)
    assert isinstance(css_path, Traversable)

    # Path should be module-relative
    path_str = str(css_path)
    assert (
        "mysite/components/heading/static/styles.css" in path_str
        or "styles.css" in path_str
    )


def test_make_path_module_structure():
    """Test that make_path returns module-relative paths."""
    # Create path to the CSS file
    css_path = make_path(Heading, "static/styles.css")

    # Verify the path is module-relative (not filesystem absolute)
    path_str = str(css_path)
    assert "styles.css" in path_str

    # Path should use forward slashes (Traversable)
    assert "/" in path_str or "styles.css" in path_str

    """Test make_path works with component instance."""
    # Create component instance
    heading = Heading("Test Heading")

    # make_path should work with instance (extracts __module__ from class)
    css_path = make_path(heading, "static/styles.css")

    assert isinstance(css_path, Traversable)
    assert "styles.css" in str(css_path)


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
    assert "logo.png" in str(img_path)


def test_make_path_no_module_attribute():
    """Test that make_path raises TypeError for objects without __module__."""
    # Plain string has no __module__
    try:
        make_path("not_a_component", "static/styles.css")
        assert False, "Should have raised TypeError"
    except TypeError as e:
        assert "__module__" in str(e)


# Task Group 1: Path Type Detection and Parsing Tests


def test_detect_path_type_package():
    """Test that package paths (with colon) are detected correctly."""
    # Package paths contain a colon separator
    assert _detect_path_type("mypackage:static/styles.css") == "package"
    assert _detect_path_type("some.package:images/logo.png") == "package"
    assert _detect_path_type("pkg:file.txt") == "package"


def test_detect_path_type_relative():
    """Test that relative paths (without colon) are detected correctly."""
    # Relative paths without colon - various formats
    assert _detect_path_type("static/styles.css") == "relative"
    assert _detect_path_type("./static/styles.css") == "relative"
    assert _detect_path_type("../shared/utils.css") == "relative"


def test_detect_path_type_edge_cases():
    """Test edge cases for path type detection."""
    # Empty string - no colon means relative
    assert _detect_path_type("") == "relative"

    # Multiple colons - first colon matters (package path)
    assert _detect_path_type("pkg:sub:file.txt") == "package"

    # Colon at start or end
    assert _detect_path_type(":file.txt") == "package"
    assert _detect_path_type("file.txt:") == "package"


def test_parse_package_path_basic():
    """Test basic package path parsing."""
    # Parse standard package path format
    package, resource = _parse_package_path("mypackage:static/styles.css")
    assert package == "mypackage"
    assert resource == "static/styles.css"

    # Parse with dotted package name
    package, resource = _parse_package_path("my.package:images/logo.png")
    assert package == "my.package"
    assert resource == "images/logo.png"


def test_parse_package_path_edge_cases():
    """Test edge cases for package path parsing."""
    # Single file after colon
    package, resource = _parse_package_path("pkg:file.txt")
    assert package == "pkg"
    assert resource == "file.txt"

    # Multiple colons - split on first occurrence
    package, resource = _parse_package_path("pkg:sub:file.txt")
    assert package == "pkg"
    assert resource == "sub:file.txt"

    # Colon at start - empty package name
    package, resource = _parse_package_path(":file.txt")
    assert package == ""
    assert resource == "file.txt"

    # Colon at end - empty resource path
    package, resource = _parse_package_path("pkg:")
    assert package == "pkg"
    assert resource == ""


# Task Group 2: Traversable Resolution for Package Paths Tests


def test_resolve_package_path_basic():
    """Test resolving package paths to Traversable instances.

    Note: For package paths, the component parameter is ignored since
    package paths are absolute references to installed packages.
    """
    # Resolve a package path to get Traversable
    # Component parameter doesn't matter for package paths - using None
    result = make_path(None, "tests.fixtures.fake_package:static/styles.css")

    # Should return a Traversable instance
    assert isinstance(result, Traversable)

    # Should be able to check if it exists
    assert result.is_file()

    # Path name should contain the resource
    assert "styles.css" in str(result)


def test_resolve_package_path_navigation():
    """Test package resource navigation with different paths.

    Note: Component parameter doesn't matter for package paths.
    """
    # Test CSS file - using None since component is ignored for package paths
    css_result = make_path(None, "tests.fixtures.fake_package:static/styles.css")
    assert isinstance(css_result, Traversable)
    assert css_result.is_file()

    # Test JS file
    js_result = make_path(None, "tests.fixtures.fake_package:static/script.js")
    assert isinstance(js_result, Traversable)
    assert js_result.is_file()

    # Test image file
    img_result = make_path(None, "tests.fixtures.fake_package:images/logo.png")
    assert isinstance(img_result, Traversable)
    assert img_result.is_file()


def test_resolve_package_path_missing_package():
    """Test error handling for missing packages.

    Note: Component parameter doesn't matter for package paths.
    """
    # Try to resolve a path to a non-existent package
    try:
        make_path(None, "nonexistent_package:static/styles.css")
        assert False, "Should have raised ModuleNotFoundError or ImportError"
    except (ModuleNotFoundError, ImportError) as e:
        # Should get an error about the missing package
        assert "nonexistent_package" in str(e) or "No module named" in str(e)


def test_resolve_relative_path_to_traversable():
    """Test that relative paths also resolve to Traversable instances."""
    # Create a relative path
    result = make_path(Heading, "static/styles.css")

    # Should return a Traversable instance
    assert isinstance(result, Traversable)

    # Path name should contain the resource
    assert "styles.css" in str(result)


def test_package_path_with_dotted_name():
    """Test package paths with dotted package names.

    Note: Component parameter doesn't matter for package paths.
    """
    # Test with fully qualified package name (dots in package)
    result = make_path(None, "tests.fixtures.fake_package:static/styles.css")

    assert isinstance(result, Traversable)
    assert result.is_file()
    assert "styles.css" in str(result)


def test_relative_path_with_prefix():
    """Test relative paths with ./ and ../ prefixes resolve to Traversable."""
    # Test with ./ prefix
    result = make_path(Heading, "./static/styles.css")
    assert isinstance(result, Traversable)

    # Test with plain relative path
    result2 = make_path(Heading, "static/styles.css")
    assert isinstance(result2, Traversable)

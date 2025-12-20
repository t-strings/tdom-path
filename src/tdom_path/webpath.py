"""Component resource path utilities for web applications.

This module provides utilities for resolving component static assets using
importlib.resources for proper package data access.

Design:
- Uses importlib.resources.files() for package resource resolution
- Returns Path object with filesystem operations (exists, read_text, etc.)
- Works with installed packages, not just src/ development directories
- Supports both development and production (wheels) environments

Integration with importlib.resources:
    from tdom_path import make_path
    from mysite.components.heading import Heading

    # Get path to component's static asset
    styles_path = make_path(Heading, "static/styles.css")
    # Returns Path object to the actual file location with filesystem operations
"""

from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import Any


def make_path(component: Any, asset: str) -> Traversable:
    """Create path to component asset using importlib.resources.

    Extracts the __module__ from the component and uses importlib.resources.files()
    to resolve the package location, then joins the asset path.

    This approach works with both development directories and installed packages (wheels),
    making it suitable for production use. Returns a Traversable path object with
    filesystem operations like .exists(), .read_text(), .is_file(), etc.

    Examples:
        >>> from mysite.components.heading import Heading
        >>> # Get path to component's CSS file
        >>> css_path = make_path(Heading, "static/styles.css")
        >>> # Returns Traversable path with filesystem operations
        >>> str(css_path)
        '.../mysite/components/heading/static/styles.css'
        >>> css_path.exists()
        True
        >>> css_path.read_text()
        '/* CSS content */'

    Args:
        component: Python object with __module__ attribute (class, function, etc.)
        asset: Relative path to the asset within the component package (e.g., "static/styles.css")

    Returns:
        Traversable path object to the resolved asset location with filesystem operations

    Raises:
        TypeError: If component doesn't have __module__ attribute
    """
    # Extract __module__ from component
    if not hasattr(component, "__module__"):
        msg = f"Object {component!r} has no __module__ attribute"
        raise TypeError(msg)

    module_name = component.__module__

    # If the module ends with a repeated component (e.g., mysite.components.heading.heading),
    # strip the last component to get the package path
    parts = module_name.split(".")
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        module_name = ".".join(parts[:-1])

    # Use importlib.resources.files() to get the package location
    package_path = files(module_name)

    # Join the asset path and return the Traversable
    return package_path / asset

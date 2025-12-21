"""Component resource path utilities for web applications.

This module provides utilities for resolving component static assets as
module-relative paths for web rendering.

Design:
- Converts Python module names to web paths (dots to slashes)
- Returns PurePosixPath for cross-platform web path consistency
- Stores paths relative to project structure (e.g., mysite/components/heading/static/styles.css)
- Works with any Python component (class, function, etc.) that has __module__

Integration:
    from tdom_path import make_path
    from mysite.components.heading import Heading

    # Get module-relative path to component's static asset
    styles_path = make_path(Heading, "static/styles.css")
    # Returns: PurePosixPath('mysite/components/heading/static/styles.css')
"""

from pathlib import PurePosixPath
from typing import Any


def make_path(component: Any, asset: str) -> PurePosixPath:
    """Create module-relative path to component asset.

    Extracts the __module__ from the component, converts it to a path
    (replacing dots with slashes), and joins the asset path.

    Returns a PurePosixPath representing the module-relative location,
    suitable for web rendering.

    Examples:
        >>> from mysite.components.heading import Heading
        >>> # Get path to component's CSS file
        >>> css_path = make_path(Heading, "static/styles.css")
        >>> str(css_path)
        'mysite/components/heading/static/styles.css'
        >>> # Use in HTML
        >>> f'<link rel="stylesheet" href="{css_path}">'
        '<link rel="stylesheet" href="mysite/components/heading/static/styles.css">'

    Args:
        component: Python object with __module__ attribute (class, function, etc.)
        asset: Relative path to the asset within the component package (e.g., "static/styles.css")

    Returns:
        PurePosixPath representing the module-relative path to the asset

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

    # Convert module name to path (replace dots with slashes)
    module_path = PurePosixPath(module_name.replace(".", "/"))

    # Join the asset path and return
    return module_path / asset

"""Component resource path utilities for web applications.

This module provides utilities for resolving component static assets as
Traversable instances for web rendering.

Design:
- Converts Python module names to web paths (dots to slashes)
- Returns Traversable for package resource access
- Stores paths relative to project structure (e.g., mysite/components/heading/static/styles.css)
- Works with any Python component (class, function, etc.) that has __module__
- Supports package asset paths using package:path syntax

Integration:
    from tdom_path import make_traversable
    from mysite.components.heading import Heading

    # Get module-relative path to component's static asset
    styles_path = make_traversable(Heading, "static/styles.css")
    # Returns: Traversable instance for mysite/components/heading/static/styles.css

    # Use package path syntax for package resources
    pkg_path = make_traversable(Heading, "mysite:static/app.js")
    # Returns: Traversable instance for mysite's static/app.js resource
"""

from functools import lru_cache
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import Any, Literal


def _detect_path_type(asset: str) -> Literal["package", "relative"]:
    """Detect whether an asset path is a package path or relative path.

    Detection logic:
    - If the path contains a colon (:), it's a package path
    - Otherwise, it's a relative path

    Args:
        asset: The asset path string to analyze

    Returns:
        "package" if the path contains a colon, "relative" otherwise

    Examples:
        >>> _detect_path_type("mysite:static/app.js")
        'package'
        >>> _detect_path_type("static/styles.css")
        'relative'
        >>> _detect_path_type("./static/styles.css")
        'relative'
        >>> _detect_path_type("../shared/utils.css")
        'relative'
    """
    return "package" if ":" in asset else "relative"


def _normalize_module_name(module_name: str) -> str:
    """Normalize module name by stripping repeated final component.

    If a module ends with a repeated component (e.g., mysite.components.heading.heading),
    strip the last component to get the package path (mysite.components.heading).

    This pattern occurs when a module defines a class with the same name as its file.

    Args:
        module_name: The module name to normalize

    Returns:
        Normalized module name with repeated component removed if present

    Examples:
        >>> _normalize_module_name("mysite.components.heading.heading")
        'mysite.components.heading'
        >>> _normalize_module_name("mysite.components.heading")
        'mysite.components.heading'
        >>> _normalize_module_name("simple")
        'simple'
    """
    parts = module_name.split(".")
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        return ".".join(parts[:-1])
    return module_name


def _parse_package_path(asset: str) -> tuple[str, str]:
    """Parse a package path into package name and resource path.

    Splits the asset string on the first colon occurrence to extract:
    - Package name (left of colon)
    - Resource path (right of colon)

    Args:
        asset: Package path string in format "package:resource/path"

    Returns:
        Tuple of (package_name, resource_path)

    Examples:
        >>> _parse_package_path("mysite:static/app.js")
        ('mysite', 'static/app.js')
        >>> _parse_package_path("mysite.components.heading:static/styles.css")
        ('mysite.components.heading', 'static/styles.css')
        >>> _parse_package_path("pkg:sub:file.txt")
        ('pkg', 'sub:file.txt')
    """
    # Split on first colon only
    parts = asset.split(":", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    # Edge case: no colon found (shouldn't happen if _detect_path_type is used first)
    return asset, ""


@lru_cache(maxsize=128)
def _get_module_files(module_name: str) -> Traversable:
    """Get cached Traversable root for a module.

    Caches the result of importlib.resources.files() to avoid repeated
    module loading overhead. This provides significant performance improvement
    when the same module is referenced multiple times.

    Args:
        module_name: Fully qualified module name (e.g., "mysite.components.heading")

    Returns:
        Traversable instance representing the module's resource root

    Examples:
        >>> root = _get_module_files("mysite.components.heading")
        >>> root2 = _get_module_files("mysite.components.heading")
        >>> root is root2
        True
    """
    return files(module_name)


def _resolve_package_path(package_name: str, resource_path: str) -> Traversable:
    """Resolve a package path to a Traversable instance.

    Uses importlib.resources.files() to get the package's Traversable root,
    then navigates to the specific resource using the / operator.

    Args:
        package_name: The Python package name (e.g., "mysite" or "mysite.components.heading")
        resource_path: The resource path within the package (e.g., "static/styles.css")

    Returns:
        Traversable instance pointing to the resource

    Raises:
        ModuleNotFoundError: If the package cannot be imported
        ImportError: If there's an issue importing the package

    Examples:
        >>> traversable = _resolve_package_path("mysite.components.heading", "static/styles.css")
        >>> traversable.is_file()
        True
    """
    # Get the package's Traversable root (cached)
    package_root = _get_module_files(package_name)

    # Navigate to the resource by splitting the path and using / operator
    # This handles paths like "static/styles.css" -> static / styles.css
    result = package_root
    if resource_path:
        for part in resource_path.split("/"):
            result = result / part

    return result


def make_traversable(component: Any, asset: str) -> Traversable:
    """Create path to component asset as a Traversable instance.

    Supports two path formats:
    1. Package paths: "package:resource/path" (e.g., "mysite:static/app.js")
       - Resolves using importlib.resources.files() to access package resources
       - Works with any installed package

    2. Relative paths: "resource/path" or "./resource/path" or "../resource/path"
       - Resolves relative to the component's module
       - Uses the component's __module__ attribute to determine the base location

    Path type detection is automatic based on presence of colon (:) character.
    If the path contains a colon, it's treated as a package path.
    Otherwise, it's treated as a relative path.

    Returns a Traversable instance representing the resource location,
    suitable for web rendering and resource access.

    Examples:
        >>> from mysite.components.heading import Heading
        >>> # Get path to component's CSS file (relative path)
        >>> css_path = make_traversable(Heading, "static/styles.css")
        >>> css_path.is_file()
        True
        >>> # Get path from a package (package path)
        >>> pkg_path = make_traversable(Heading, "mysite:static/app.js")
        >>> pkg_path.is_file()
        True

    Args:
        component: Python object with __module__ attribute (class, function, etc.)
        asset: Path to the asset. Can be:
               - Package path: "package:resource/path"
               - Relative path: "resource/path", "./resource/path", or "../resource/path"

    Returns:
        Traversable instance representing the resource location

    Raises:
        TypeError: If component doesn't have __module__ attribute
        ModuleNotFoundError: If a package path references a non-existent package
        ImportError: If there's an issue importing a package
    """
    # Detect path type first - package paths don't need the component
    path_type = _detect_path_type(asset)

    if path_type == "package":
        # Parse and resolve package path
        # Component is not needed for package paths
        package_name, resource_path = _parse_package_path(asset)
        return _resolve_package_path(package_name, resource_path)
    else:
        # For relative paths, we need the component's __module__
        if not hasattr(component, "__module__"):
            msg = f"Object {component!r} has no __module__ attribute"
            raise TypeError(msg)
        # Resolve relative path using component's module
        module_name = _normalize_module_name(component.__module__)

        # Get the component module's Traversable root (cached)
        module_root = _get_module_files(module_name)

        # Navigate to the asset using / operator
        # Handle paths with ./ prefix by stripping it
        clean_asset = asset.lstrip("./")

        # Split path and navigate using Traversable's / operator
        result = module_root
        for part in clean_asset.split("/"):
            if part:  # Skip empty parts
                result = result / part

        return result

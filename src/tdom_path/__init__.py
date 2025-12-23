"""tdom-path: Component resource path utilities for web applications.

This library provides utilities for resolving component static assets (CSS, JS, images)
as module-relative PurePosixPath objects for web rendering.

Phase 1: Core Path API - make_traversable converts module names to web paths
Phase 2: Tree Rewriting - make_path_nodes for automatic asset resolution
Phase 3: Path Rendering - render_path_nodes for relative path string conversion
"""

from tdom_path.tree import make_path_nodes, path_nodes, render_path_nodes
from tdom_path.webpath import make_traversable

__all__ = ["make_traversable", "make_path_nodes", "path_nodes", "render_path_nodes"]

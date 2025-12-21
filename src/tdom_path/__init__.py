"""tdom-path: Component resource path utilities for web applications.

This library provides utilities for resolving component static assets (CSS, JS, images)
using importlib.resources for proper package data access.

Phase 1: Core Path API - make_path with importlib.resources integration
Phase 2: Tree Rewriting - make_path_nodes for automatic asset resolution
"""

from tdom_path.tree import make_path_nodes, path_nodes
from tdom_path.webpath import make_path

__all__ = ["make_path", "make_path_nodes", "path_nodes"]

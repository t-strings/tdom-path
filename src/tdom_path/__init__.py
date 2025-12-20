"""tdom-path: Component resource path utilities for web applications.

This library provides utilities for resolving component static assets (CSS, JS, images)
using importlib.resources for proper package data access.

Phase 1: Core Path API - make_path with importlib.resources integration
"""

from tdom_path.webpath import make_path

__all__ = ["make_path"]

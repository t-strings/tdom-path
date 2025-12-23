"""Root pytest configuration with Sybil doctest integration.

Handles:
- src/*.py: Python docstrings with DocTestParser
- README.md: Markdown with PythonCodeBlockParser

Note: docs/*.md files are handled by docs/conftest.py

WARNING: Python 3.14 (both free-threaded and non-free-threaded) has a recursion
bug in doctest's __patched_linecache_getlines (line 1507). The bug triggers when
pytest+Sybil tries to format error messages for failed doctests. Tests will pass
until a failure occurs, then pytest will crash with RecursionError.

Workaround if needed: Use `python -m doctest src/tdom_path/*.py` directly.
"""

from sybil import Sybil
from sybil.parsers.myst import PythonCodeBlockParser
from sybil.parsers.rest import DocTestParser

# Import here to avoid duplication with docs/conftest.py
# These are only needed for README.md
from pathlib import PurePosixPath
from typing import Protocol
from importlib.resources.abc import Traversable
from tdom import Element, html
from tdom_path import make_traversable, make_path_nodes, path_nodes, render_path_nodes
from tdom_path.tree import RelativePathStrategy


# Mock Heading class - points to examples/mysite/components/heading
class Heading:
    __module__ = "mysite.components.heading"


# Configure Sybil for src/ Python files (minimal globals)
_sybil_src = Sybil(
    parsers=[DocTestParser()],
    patterns=["*.py"],
    path="src",
    setup=lambda ns: ns.update({"Heading": Heading}),
)

# Configure Sybil for README.md (comprehensive globals)
_sybil_readme = Sybil(
    parsers=[PythonCodeBlockParser()],
    patterns=["README.md"],
    path=".",
    setup=lambda ns: ns.update(
        {
            "Heading": Heading,
            "Element": Element,
            "html": html,
            "make_traversable": make_traversable,
            "make_path_nodes": make_path_nodes,
            "render_path_nodes": render_path_nodes,
            "path_nodes": path_nodes,
            "RelativePathStrategy": RelativePathStrategy,
            "PurePosixPath": PurePosixPath,
            "Protocol": Protocol,
            "Traversable": Traversable,
        }
    ),
)

# Combine hooks
_src_hook = _sybil_src.pytest()
_readme_hook = _sybil_readme.pytest()


def pytest_collect_file(file_path, parent):
    """Collect from src/ and README.md."""
    return _src_hook(file_path, parent) or _readme_hook(file_path, parent)

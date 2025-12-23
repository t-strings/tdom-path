"""Pytest configuration for docs/ markdown doctests.

This conftest handles docs/**/*.md only (README.md is in root conftest.py)
Uses PythonCodeBlockParser to parse ```python blocks containing doctest syntax.
"""

from pathlib import PurePosixPath
from typing import Protocol
from importlib.resources.abc import Traversable

from sybil import Sybil
from sybil.parsers.myst import PythonCodeBlockParser
from tdom import Element, html
from tdom_path import make_traversable, make_path_nodes, path_nodes, render_path_nodes
from tdom_path.tree import RelativePathStrategy


# Mock Heading class
class Heading:
    __module__ = "mysite.components.heading"


# Configure Sybil for docs/ markdown files
pytest_collect_file = Sybil(
    parsers=[PythonCodeBlockParser()],
    patterns=["*.md"],
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
).pytest()

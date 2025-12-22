"""Performance benchmarks for tdom-path library operations.

Consolidated performance suite measuring time and memory.
"""

import time
import tracemalloc
from pathlib import PurePosixPath
from importlib.resources.abc import Traversable

import pytest
from tdom import Element, Fragment, html

from mysite.components.heading import Heading
from tdom_path import make_path, make_path_nodes, render_path_nodes
from tdom_path.tree import _walk_tree


@pytest.fixture
def large_tree():
    """Realistic component tree for scale testing."""
    sections = []
    for s in range(10):
        sub = []
        for ss in range(3):
            articles = []
            for a in range(4):
                articles.append(html(t"""<article><div><p></p><span></span></div></article>"""))
            sub.append(html(t"""<section>{articles}</section>"""))
        sections.append(html(t"""<div>{sub}</div>"""))

    return html(t"""<html>
        <head>
            <link rel="stylesheet" href="static/styles.css" />
            <link rel="stylesheet" href="static/theme.css" />
            <link rel="stylesheet" href="static/base.css" />
            <script src="static/app.js"></script>
        </head>
        <body>{sections}</body>
    </html>""")


@pytest.mark.slow
@pytest.mark.freethreaded(threads=1, iterations=1)
def test_performance_metrics(large_tree):
    """Consolidated performance measurements avoiding plugin conflicts."""
    target = PurePosixPath("index.html")
    path_tree = make_path_nodes(large_tree, Heading)
    
    def run_suite():
        make_path(Heading, "static/styles.css")
        make_path_nodes(large_tree, Heading)
        render_path_nodes(path_tree, target)
        _walk_tree(large_tree, lambda n: n)

    # 1. Execution time (Average over 100 runs)
    iterations = 100
    start = time.perf_counter()
    for _ in range(iterations):
        run_suite()
    end = time.perf_counter()
    print(f"\nAvg execution time: {(end - start) / iterations * 1000:.3f} ms")

    # 2. Peak memory
    if not tracemalloc.is_tracing():
        tracemalloc.start()
    s1 = tracemalloc.take_snapshot()
    run_suite()
    s2 = tracemalloc.take_snapshot()
    mem = sum(s.size_diff for s in s2.compare_to(s1, 'lineno'))
    tracemalloc.stop()
    print(f"Memory usage delta: {mem / 1024:.2f} KB")

    # 3. Sanity check
    assert isinstance(make_path(Heading, "static/styles.css"), Traversable)
    assert make_path_nodes(large_tree, Heading) is not None

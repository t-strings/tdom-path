#!/usr/bin/env python
"""Quick performance benchmark for tdom-path operations.

Run this before and after optimizations to measure improvements.
"""

import sys
import time
from pathlib import PurePosixPath

# Add examples to path for Heading component
sys.path.insert(0, "examples")

from tdom import html

from mysite.components.heading import Heading
from tdom_path import make_path, make_path_nodes, render_path_nodes
from tdom_path.tree import _walk_tree


def create_test_tree():
    """Create a medium-sized tree for benchmarking."""
    sections = []
    for s in range(10):
        subsections = []
        for ss in range(3):
            articles = []
            for a in range(4):
                articles.append(
                    html(t"""
                        <article>
                            <div>
                                <p>Content {a}</p>
                                <span>Meta</span>
                            </div>
                        </article>
                    """)
                )
            subsections.append(html(t"""<section>{articles}</section>"""))
        sections.append(html(t"""<div>{subsections}</div>"""))

    return html(t"""<html>
        <head>
            <link rel="stylesheet" href="static/styles.css" />
            <link rel="stylesheet" href="static/theme.css" />
            <link rel="stylesheet" href="static/base.css" />
            <script src="static/app.js"></script>
            <script src="static/script.js"></script>
        </head>
        <body>
            <nav>
                <a href="index.html">Home</a>
                <a href="about.html">About</a>
            </nav>
            <main>{sections}</main>
        </body>
    </html>""")


def benchmark_operation(name: str, operation, iterations: int = 100):
    """Benchmark a single operation."""
    # Warmup to ensure JIT compilation, etc.
    for _ in range(10):
        result = operation()

    start = time.perf_counter()
    for _ in range(iterations):
        result = operation()
        # Prevent optimization by accessing result
        _ = result
    end = time.perf_counter()

    total_time = (end - start) * 1_000_000  # Convert to microseconds
    avg_time = total_time / iterations

    print(f"  {name:<35} {avg_time:>10.3f}μs/op  ({iterations} iterations)")
    return avg_time


def run_benchmark():
    """Run all benchmarks."""
    print("=" * 85)
    print("TDOM-PATH PERFORMANCE BENCHMARK")
    print("=" * 85)

    print("\nCreating test tree...")
    tree = create_test_tree()
    print("✓ Tree created (120+ components)\n")

    print("Running benchmarks...")
    print("-" * 85)

    results = {}

    # Path resolution benchmarks
    results["make_path"] = benchmark_operation(
        "make_path() - relative path",
        lambda: make_path(Heading, "static/styles.css"),
    )

    results["make_path_pkg"] = benchmark_operation(
        "make_path() - package path",
        lambda: make_path(None, "tests.fixtures.fake_package:static/styles.css"),
    )

    # Tree transformation benchmarks
    results["make_path_nodes"] = benchmark_operation(
        "make_path_nodes() - tree transform",
        lambda: make_path_nodes(tree, Heading),
        iterations=50,  # Slower operation, fewer iterations
    )

    # Pre-transform tree for rendering benchmark
    print("\n  [Preparing transformed tree for render benchmark...]")
    path_tree = make_path_nodes(tree, Heading)
    target = PurePosixPath("mysite/pages/index.html")

    results["render_path_nodes"] = benchmark_operation(
        "render_path_nodes() - path rendering",
        lambda: render_path_nodes(path_tree, target),
        iterations=50,
    )

    # Tree traversal benchmark
    results["walk_tree"] = benchmark_operation(
        "_walk_tree() - traversal only",
        lambda: _walk_tree(tree, lambda node: node),
        iterations=50,
    )

    print("-" * 85)
    print(f"\nAverage time per operation: {sum(results.values()) / len(results):.3f}μs")
    print("\n" + "=" * 85)
    print("Benchmark complete!")
    print("=" * 85)

    # Performance targets
    print("\nPerformance Analysis:")
    print("-" * 85)

    # Path resolution (fast operations)
    path_ops = [results["make_path"], results["make_path_pkg"]]
    avg_path = sum(path_ops) / len(path_ops)
    print(f"\n  Path Resolution: {avg_path:.1f}μs/op")
    if avg_path < 10:
        print("    ✓ EXCELLENT - Path resolution is very fast")
    elif avg_path < 50:
        print("    ✓ GOOD - Acceptable path resolution speed")
    else:
        print("    ⚠ Consider optimization for path resolution")

    # Tree operations (slower operations)
    tree_ops = [results["make_path_nodes"], results["render_path_nodes"], results["walk_tree"]]
    avg_tree = sum(tree_ops) / len(tree_ops)
    print(f"\n  Tree Operations: {avg_tree:.1f}μs/op")
    if avg_tree < 100:
        print("    ✓ EXCELLENT - Tree operations are very fast")
    elif avg_tree < 500:
        print("    ✓ GOOD - Tree operations are efficient")
    elif avg_tree < 1000:
        print("    ⚠ FAIR - Consider optimization for large trees")
    else:
        print("    ✗ SLOW - Optimization recommended")

    print(f"\n  Overall Average: {sum(results.values()) / len(results):.1f}μs/op")
    print("\n" + "=" * 85)


def main():
    """CLI entry point."""
    run_benchmark()


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Quick performance benchmark for tdom-path operations.

Run this before and after optimizations to measure improvements.
"""

import sys
import time
from pathlib import PurePosixPath


from tdom import html

from tdom_path import make_path_nodes, render_path_nodes, make_traversable
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


def benchmark_operation(
    name: str, operation, iterations: int = 100, warmup: bool = True
):
    """Benchmark a single operation."""
    # Warmup to ensure JIT compilation, etc. (but skip for cold cache tests)
    if warmup:
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

    print(f"  {name:<45} {avg_time:>10.3f}μs/op  ({iterations} iterations)")
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

    # Path resolution benchmarks - COLD CACHE
    print("\n  [Cold cache tests - measuring first-time module loading...]")
    from tdom_path.webpath import _get_module_files

    _get_module_files.cache_clear()  # Clear cache for cold test

    # Add examples to path for Heading component
    sys.path.insert(0, "examples")
    from mysite.components.heading import Heading

    results["make_path_cold"] = benchmark_operation(
        "make_path() - relative (COLD cache)",
        lambda: make_traversable(Heading, "static/styles.css"),
        iterations=100,
        warmup=False,  # No warmup for cold cache test
    )

    # Path resolution benchmarks - WARM CACHE (realistic scenario)
    print("\n  [Warm cache tests - simulating repeated use...]")
    results["make_path"] = benchmark_operation(
        "make_path() - relative (WARM cache)",
        lambda: make_traversable(Heading, "static/styles.css"),
    )

    results["make_path_pkg"] = benchmark_operation(
        "make_path() - package path (WARM)",
        lambda: make_traversable(None, "tests.fixtures.fake_package:static/styles.css"),
    )

    # SSG Simulation: Transform same tree for multiple pages
    print("\n  [SSG workflow: transforming component tree...]")
    results["make_path_nodes"] = benchmark_operation(
        "make_path_nodes() - tree transform",
        lambda: make_path_nodes(tree, Heading),
        iterations=50,
    )

    # Pre-transform tree for rendering benchmark
    print("\n  [Preparing transformed tree for multi-page rendering...]")
    path_tree = make_path_nodes(tree, Heading)

    # SSG Simulation: Render for multiple target pages
    targets = [
        PurePosixPath("mysite/index.html"),
        PurePosixPath("mysite/pages/about.html"),
        PurePosixPath("mysite/pages/docs/guide.html"),
        PurePosixPath("mysite/blog/post1.html"),
    ]

    results["render_multi_page"] = benchmark_operation(
        "render_path_nodes() - 4 pages (SSG scenario)",
        lambda: [render_path_nodes(path_tree, target) for target in targets],
        iterations=25,
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

    # Cache impact analysis
    cache_speedup = (results["make_path_cold"] / results["make_path"] - 1) * 100
    print("\n  LRU Cache Impact:")
    print(
        f"    Cold cache:  {results['make_path_cold']:.1f}μs/op (first module access)"
    )
    print(f"    Warm cache:  {results['make_path']:.1f}μs/op (cached module)")
    print(
        f"    Speedup:     {cache_speedup:.0f}% faster with cache ({results['make_path_cold'] / results['make_path']:.1f}x)"
    )
    if cache_speedup > 500:
        print("    ✓ EXCELLENT - Cache providing massive performance boost")
    elif cache_speedup > 100:
        print("    ✓ GOOD - Cache significantly improves performance")
    elif cache_speedup > 20:
        print("    ✓ FAIR - Cache helping performance")
    else:
        print("    ⚠ Cache not providing significant benefit")

    # Path resolution (warm cache - typical usage)
    path_ops = [results["make_path"], results["make_path_pkg"]]
    avg_path = sum(path_ops) / len(path_ops)
    print(f"\n  Path Resolution (warm cache): {avg_path:.1f}μs/op")
    if avg_path < 10:
        print("    ✓ EXCELLENT - Path resolution is very fast")
    elif avg_path < 50:
        print("    ✓ GOOD - Acceptable path resolution speed")
    else:
        print("    ⚠ Consider optimization for path resolution")

    # SSG rendering (multi-page scenario)
    avg_per_page = results["render_multi_page"] / 4  # 4 pages per iteration
    print("\n  SSG Rendering (4 pages per iteration):")
    print(f"    Total:    {results['render_multi_page']:.1f}μs/op (4 pages)")
    print(f"    Per page: {avg_per_page:.1f}μs/page")
    if avg_per_page < 200:
        print("    ✓ EXCELLENT - Fast multi-page rendering")
    elif avg_per_page < 500:
        print("    ✓ GOOD - Efficient multi-page rendering")
    else:
        print("    ⚠ Consider optimization for SSG workflows")

    print(f"\n  Overall Average: {sum(results.values()) / len(results):.1f}μs/op")
    print("\n" + "=" * 85)


def main():
    """CLI entry point."""
    run_benchmark()


if __name__ == "__main__":
    main()

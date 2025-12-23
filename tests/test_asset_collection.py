"""Tests for asset collection feature.

These tests verify the AssetReference dataclass and collected_assets
attribute on RelativePathStrategy.
"""

from pathlib import PurePosixPath

from aria_testing import get_by_tag_name
from tdom import html
from mysite.components.heading import Heading
from tdom_path.tree import (
    AssetReference,
    RelativePathStrategy,
    make_path_nodes,
    render_path_nodes,
)
from tdom_path.webpath import make_path


# ============================================================================
# Task Group 1: AssetReference Dataclass and Strategy Modification Tests
# ============================================================================


def test_asset_reference_deduplication():
    """Test AssetReference deduplicates in sets based on module_path."""
    # Same module_path deduplicates
    source1 = make_path(Heading, "static/styles.css")
    source2 = make_path(Heading, "static/styles.css")
    module_path = PurePosixPath("mysite/components/heading/static/styles.css")

    ref1 = AssetReference(source=source1, module_path=module_path)
    ref2 = AssetReference(source=source2, module_path=module_path)

    asset_set = {ref1, ref2}
    assert len(asset_set) == 1  # Deduplicates

    # Different module_paths don't deduplicate
    source3 = make_path(Heading, "static/app.js")
    module_path2 = PurePosixPath("mysite/components/heading/static/app.js")
    ref3 = AssetReference(source=source3, module_path=module_path2)

    asset_set.add(ref3)
    assert len(asset_set) == 2  # Different path, no deduplication


def test_strategy_collected_assets():
    """Test RelativePathStrategy.collected_assets accumulates assets."""
    strategy = RelativePathStrategy()
    assert len(strategy.collected_assets) == 0

    # Add assets to collected_assets
    source = make_path(Heading, "static/styles.css")
    module_path = PurePosixPath("mysite/components/heading/static/styles.css")
    ref = AssetReference(source=source, module_path=module_path)
    strategy.collected_assets.add(ref)
    assert len(strategy.collected_assets) == 1


# ============================================================================
# Task Group 2: Asset Collection During Rendering Tests
# ============================================================================


def test_rendering_collects_assets():
    """Test assets are collected during rendering with proper deduplication."""
    # Single asset collected
    tree = html(t"""<link href="static/styles.css">""")
    path_tree = make_path_nodes(tree, Heading)
    strategy = RelativePathStrategy()
    target = PurePosixPath("mysite/pages/index.html")
    result = render_path_nodes(path_tree, target, strategy)

    assert len(strategy.collected_assets) == 1
    collected_ref = next(iter(strategy.collected_assets))
    assert collected_ref.module_path == PurePosixPath(
        "mysite/components/heading/static/styles.css"
    )

    # Rendering still produces string paths
    link = get_by_tag_name(result, "link")
    assert isinstance(link.attrs["href"], str)

    # Multiple assets in single rendering
    tree2 = html(t"""
        <link href="static/styles.css">
        <script src="static/app.js"></script>
    """)
    path_tree2 = make_path_nodes(tree2, Heading)
    strategy2 = RelativePathStrategy()
    render_path_nodes(path_tree2, target, strategy2)
    assert len(strategy2.collected_assets) == 2

    # Multiple renderings accumulate assets
    tree3 = html(t"""<script src="static/theme.css"></script>""")
    path_tree3 = make_path_nodes(tree3, Heading)
    render_path_nodes(path_tree3, target, strategy2)
    assert len(strategy2.collected_assets) == 3

    # Deduplication across pages
    strategy3 = RelativePathStrategy()
    render_path_nodes(path_tree, PurePosixPath("mysite/pages/index.html"), strategy3)
    render_path_nodes(path_tree, PurePosixPath("mysite/pages/about.html"), strategy3)
    assert len(strategy3.collected_assets) == 1  # Same asset, deduplicated


def test_collection_edge_cases():
    """Test collection edge cases: external URLs and site_prefix."""
    # External URLs should not be collected
    tree = html(t"""<link href="https://external.com/styles.css">""")
    path_tree = make_path_nodes(tree, Heading)
    strategy = RelativePathStrategy()
    target = PurePosixPath("mysite/pages/index.html")
    render_path_nodes(path_tree, target, strategy)
    assert len(strategy.collected_assets) == 0  # External URL not collected

    # site_prefix doesn't affect collection
    tree2 = html(t"""<link href="static/styles.css">""")
    path_tree2 = make_path_nodes(tree2, Heading)
    strategy2 = RelativePathStrategy(site_prefix=PurePosixPath("mysite/static"))
    result = render_path_nodes(path_tree2, target, strategy2)
    assert len(strategy2.collected_assets) == 1  # Asset still collected
    link = get_by_tag_name(result, "link")
    href = link.attrs["href"]
    assert href is not None  # Ensure href is not None
    assert "mysite/static" in href  # site_prefix in rendered path


# ============================================================================
# Task Group 3: Test Review & Gap Analysis - Strategic Integration Tests
# ============================================================================


def test_collected_assets_for_build_tools():
    """Test end-to-end workflow for build tools: collect assets and read contents."""
    tree = html(t"""
        <link href="static/styles.css">
        <script src="static/app.js"></script>
    """)

    path_tree = make_path_nodes(tree, Heading)
    strategy = RelativePathStrategy()
    target = PurePosixPath("mysite/pages/index.html")
    rendered_tree = render_path_nodes(path_tree, target, strategy)

    # Assets collected with correct module paths
    assert len(strategy.collected_assets) == 2
    module_paths = {ref.module_path for ref in strategy.collected_assets}
    assert PurePosixPath("mysite/components/heading/static/styles.css") in module_paths
    assert PurePosixPath("mysite/components/heading/static/app.js") in module_paths

    # Can read file contents from collected assets
    for asset_ref in strategy.collected_assets:
        content = asset_ref.source.read_bytes()
        assert isinstance(content, bytes)
        assert len(content) > 0

    # Rendered tree has string paths
    link = get_by_tag_name(rendered_tree, "link")
    assert isinstance(link.attrs["href"], str)


def test_build_tool_simulation():
    """Test simulating a build tool copying collected assets to output directory."""
    from pathlib import Path
    import tempfile

    tree = html(t"""
        <link href="static/styles.css">
        <script src="static/app.js"></script>
    """)

    path_tree = make_path_nodes(tree, Heading)
    strategy = RelativePathStrategy()
    target = PurePosixPath("mysite/pages/index.html")
    render_path_nodes(path_tree, target, strategy)

    # Simulate build tool: copy assets to temporary build directory
    with tempfile.TemporaryDirectory() as build_dir:
        build_path = Path(build_dir)

        for asset_ref in strategy.collected_assets:
            content = asset_ref.source.read_bytes()
            dest_path = build_path / asset_ref.module_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(content)

            # Verify file written correctly with nested dirs preserved
            assert dest_path.exists()
            assert dest_path.read_bytes() == content

        # Verify both assets were copied
        copied_files = [f.name for f in build_path.rglob("*") if f.is_file()]
        assert "styles.css" in copied_files
        assert "app.js" in copied_files

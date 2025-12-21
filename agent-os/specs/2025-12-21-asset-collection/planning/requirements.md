# Spec Requirements: Asset Collection

## Initial Description

Feature request for implementing roadmap item #7: Asset Collection

**From roadmap:**
"In the pluggable implementation `RelativePathStrategy` implement a way to collect Traversable asset instances that need to be copied to the output. Add `resolved_assets: set[Traversable]` (or whatever is the correct type). Then make sure a single instance of `ResolvedAsset` can be re-used for multiple renderings."

**Context:**
- Follows completed features: Core Path API, Tree Rewriting for Assets, Path Element, Path Rendering, and Traversable/package specs support
- Project provides component resource path utilities for web applications using tdom Node structures
- Uses Python 3.14+, tdom for HTML tree structures, and importlib.resources for package asset resolution
- Current implementation transforms paths from strings to PurePosixPath objects in Node trees, then renders them relative to targets

## Requirements Discussion

### First Round Questions

**Q1:** Where in the rendering pipeline should asset collection happen?
**Answer:** Collection should happen in `_render_transform_node()` or `render_path_nodes()` before converting _TraversableWithPath to string. This is the point where we have access to the TraversableElement with its _TraversableWithPath wrapper before it gets converted to a relative path string.

**Q2:** What data structure should be used for the collected assets?
**Answer:** Set of dataclasses. Specifically, an `AssetReference` dataclass containing:
- `source`: The Traversable instance (from `traversable._traversable`)
- `module_path`: The PurePosixPath representing the destination path (from `traversable._module_path`)

**Q3:** How should deduplication work for the same asset referenced multiple times?
**Answer:** Either option 1 (frozen dataclass with hash based on module_path) or option 2 (custom __hash__ and __eq__ methods), whichever is easiest to implement. The key requirement is that assets with the same module_path should deduplicate automatically when added to the set.

**Q4:** Should RelativePathStrategy.collected_assets be a read-only property or have explicit add/clear methods?
**Answer:** No methods needed - simple attribute access is sufficient. The collection will happen internally during rendering, and consumers just need to read the set after rendering completes.

**Q5:** Should we validate that URLs are local before collecting them?
**Answer:** Not needed because TraversableElement is only created for local paths. External URLs are already filtered out by the existing `_should_process_href()` logic, so anything that becomes a TraversableElement is by definition a local asset that needs collecting.

### Existing Code to Reference

**Similar Features Identified:**
- Feature: RelativePathStrategy - Path: `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`
- Components to potentially reuse: The existing `render_path_nodes()` and `_render_transform_node()` functions that walk the tree and transform TraversableElement nodes
- Backend logic to reference: The _TraversableWithPath wrapper class that already contains both `._traversable` (Traversable instance) and `._module_path` (PurePosixPath) - all the information needed for collection

### Follow-up Questions

None - requirements are clear from the initial answers.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A - This is a data collection feature without UI components.

## Requirements Summary

### Functional Requirements

**Core Functionality:**
- Collect Traversable asset instances during path rendering that need to be copied to build output
- Store collected assets in a deduplicated set on the RelativePathStrategy instance
- Preserve both the source Traversable (for reading file contents) and the module_path (for determining destination)
- Enable single RelativePathStrategy instance to be reused for multiple renderings
- Provide simple attribute access to collected assets for build tools/SSGs

**Data Collection:**
- Extract from _TraversableWithPath wrapper: `._traversable` and `._module_path`
- Collection trigger: During `_render_transform_node()` or `render_path_nodes()` before converting wrapper to string
- No modification to _TraversableWithPath needed - it already has all required information

**Integration Point:**
- Modify RelativePathStrategy class to add `collected_assets` attribute
- Insert collection logic in the rendering pipeline where TraversableElement nodes are processed
- Ensure collection happens before path conversion to string (while we still have wrapper object)

### API Design

**New Dataclass:**
```python
@dataclass(frozen=True)
class AssetReference:
    """Reference to a collected asset with source and destination information."""
    source: Traversable  # For reading file contents via .read_bytes()
    module_path: PurePosixPath  # For determining build directory destination
```

**Modified Class:**
```python
class RelativePathStrategy:
    collected_assets: set[AssetReference]  # Set for automatic deduplication
    # ... existing methods ...
```

**Hashability Approach:**
- Either use `frozen=True` dataclass (option 1) with hash based on module_path string
- Or implement custom `__hash__` and `__eq__` methods (option 2)
- Whichever is easier - both provide the same deduplication behavior

### Reusability Opportunities

**Existing Components to Leverage:**
- `_TraversableWithPath` wrapper - already contains all needed data (`._traversable`, `._module_path`)
- `render_path_nodes()` - main entry point for rendering, iterates through tree
- `_render_transform_node()` - processes individual TraversableElement nodes
- `TraversableElement` - identifies nodes that reference local assets

**No Changes Needed:**
- The data capture mechanism (_TraversableWithPath) is already complete
- Just need to extract and store the data during rendering

### Scope Boundaries

**In Scope:**
- Add `collected_assets` attribute to RelativePathStrategy
- Create AssetReference dataclass with source Traversable and module_path
- Implement collection logic in rendering pipeline (before path-to-string conversion)
- Ensure deduplication via set and hashability
- Support reusing strategy instance across multiple renders
- Simple attribute access to collected assets (no methods needed)

**Out of Scope:**
- Actually copying files to build directory (responsibility of SSG/build tool)
- File I/O operations or filesystem manipulation
- Validation of whether assets exist (existing code handles this)
- URL filtering (already handled by _should_process_href)
- Complex API with add/clear/query methods

### Technical Considerations

**Integration Points:**
- Collection happens in `_render_transform_node()` or `render_path_nodes()`
- Must occur before `_TraversableWithPath` is converted to string
- Accessed by SSG build tools after rendering completes

**Existing System Patterns:**
- Uses dataclasses throughout codebase
- Set-based deduplication is standard pattern
- Simple attribute access over complex APIs
- Traversable from importlib.resources for package assets

**Technology Preferences:**
- Python 3.14+ with type hints
- Frozen dataclass or custom __hash__/__eq__ for hashability
- Standard library only (no additional dependencies)

**Build Tool Usage Example:**
```python
# SSG build tool usage:
strategy = RelativePathStrategy(target=PurePosixPath("index.html"))
rendered_html = render_path_nodes(node_tree, strategy)

# After rendering, collect assets for copying
for asset_ref in strategy.collected_assets:
    content = asset_ref.source.read_bytes()
    dest_path = build_dir / asset_ref.module_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(content)
```

### Implementation Location

**Primary File:** `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`

**Key Points:**
- Modify `RelativePathStrategy` class to add `collected_assets: set[AssetReference]`
- Create `AssetReference` dataclass near top of file
- Add collection logic in `_render_transform_node()` before path conversion
- Initialize `collected_assets` as empty set in `__init__` or as class attribute

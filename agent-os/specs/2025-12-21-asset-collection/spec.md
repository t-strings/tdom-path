# Specification: Asset Collection

## Goal

Enable SSG build tools to collect and copy Traversable assets referenced in HTML trees by automatically tracking them
during path rendering, supporting reusable rendering strategies across multiple pages.

## User Stories

- As an SSG developer, I want to automatically collect all asset references during rendering so that I can copy them to
  the build directory without manual tracking
- As a build tool author, I want to reuse a single RelativePathStrategy instance across multiple page renders so that I
  can efficiently collect all assets from an entire site

## Specific Requirements

**Add AssetReference dataclass to store collected assets**

- Create frozen dataclass with `source: Traversable` (for reading file contents) and `module_path: PurePosixPath` (for
  destination path)
- Implement hashability using frozen=True dataclass with hash based on module_path string representation
- Place near top of tree.py with other dataclass definitions
- Import PurePosixPath and Traversable types at module level

**Add collected_assets attribute to RelativePathStrategy**

- Add `collected_assets: set[AssetReference]` as class attribute or initialize in __init__
- Set provides automatic deduplication when same asset referenced multiple times
- No public methods needed - consumers access attribute directly after rendering
- Strategy instance can be reused across multiple render_path_nodes() calls to accumulate assets

**Modify _render_transform_node to collect assets during rendering**

- Extract source Traversable and module_path from _TraversableWithPath wrapper before path conversion
- Access `traversable._traversable` for source and `traversable._module_path` for destination
- Create AssetReference instance and add to strategy.collected_assets set
- Collection happens before calculating string path representation
- No changes needed to return value or function signature

**Integrate collection logic with existing rendering pipeline**

- Collection occurs in _render_transform_node() when processing TraversableElement nodes
- Only collect when isinstance(attr_value, Traversable) is True
- Access strategy instance via passed parameter to add to collected_assets
- Maintains existing immutability guarantees - collection is side effect on strategy object

**Support strategy reuse across multiple renderings**

- Single RelativePathStrategy instance can be passed to multiple render_path_nodes() calls
- Each rendering adds new assets to the same collected_assets set
- Set automatically deduplicates if same asset appears in multiple pages
- Build tools can iterate collected_assets once after all pages rendered

## Existing Code to Leverage

**_TraversableWithPath wrapper class**

- Already contains both `._traversable` (source Traversable) and `._module_path` (destination PurePosixPath)
- No modifications needed - simply extract these attributes during collection
- Wrapper is detected via isinstance(attr_value, Traversable) check in _render_transform_node()

**_render_transform_node() function**

- Currently processes TraversableElement nodes and converts Traversable attributes to strings
- Already iterates over node.attrs.items() checking isinstance(attr_value, Traversable)
- Add collection logic before strategy.calculate_path() call
- Strategy parameter already available as function argument

**render_path_nodes() function**

- Entry point that creates default RelativePathStrategy() if none provided
- Strategy instance passed through to _render_transform_node() via lambda
- No changes needed - collection happens automatically in helper function

**RelativePathStrategy dataclass**

- Currently frozen=True with site_prefix optional attribute
- Need to make mutable (remove frozen=True) to support collected_assets set
- Or use field(default_factory=set) with frozen=False
- Maintains existing calculate_path() method unchanged

**make_path_nodes() and TraversableElement**

- These create the _TraversableWithPath wrappers that collection extracts from
- No changes needed - collection is downstream in rendering pipeline
- TraversableElement identifies which nodes contain Traversable attributes

## Out of Scope

- Actually copying files to build directory (responsibility of SSG tool, not tdom-path)
- File I/O operations or filesystem manipulation
- Validation of whether collected assets exist (already handled by make_path_nodes)
- URL filtering or external link handling (already handled by _should_process_href)
- Public methods for adding/clearing/querying collected_assets manually
- Custom collection strategies or pluggable collectors
- Collection reporting or statistics
- Progress tracking or logging during collection
- Batch processing or parallel collection
- Asset transformation or optimization during collection

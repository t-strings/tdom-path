# Specification: Path Rendering

## Goal

Create a `render_path_nodes()` function that walks a tdom tree, detects `PathElement` nodes with `PurePosixPath`
attribute values, and transforms them into regular `Element` nodes with relative path strings calculated based on a
target path.

## User Stories

- As a static site generator, I want to transform `PathElement` nodes containing `PurePosixPath` paths into regular
  `Element` nodes with relative path strings so that the HTML output contains correct relative links between pages
- As a developer, I want a flexible strategy pattern for path rendering so that I can customize how paths are calculated
  for different deployment scenarios (relative paths, absolute paths, CDN URLs, etc.)

## Specific Requirements

**Core Function Signature**

- Function named
  `render_path_nodes(tree: Node, target: PurePosixPath, strategy: RenderStrategy | None = None)`
- Takes a tdom Node tree as first parameter
- Takes a `PurePosixPath` (not `PurePath`) as target parameter representing the output location
- Takes an optional strategy parameter with `RelativePathStrategy` as the default
- Returns a new immutable Node tree with transformations applied
- Optimizes to return the same object reference when no transformations are needed

**PathElement Detection**

- Use `isinstance(node, PathElement)` to detect elements that may contain PurePosixPath paths
- Inspect all attributes of detected `PathElement` nodes
- Check each attribute value using `isinstance(value, PurePosixPath)` to find PurePosixPath instances
- Process any attribute that contains a PurePosixPath value, not just `href` and `src`

**Element Transformation**

- Convert detected `PathElement` nodes into regular `Element` instances
- Replace `PurePosixPath` attribute values with string representations calculated by the strategy
- Preserve all other attributes unchanged (tag, children, non-PurePosixPath attrs)
- Maintain element structure and hierarchy in the output tree

**RenderStrategy Protocol**

- Define a Protocol-based interface named `RenderStrategy`
- Protocol requires a method with signature: `calculate_path(source: PurePosixPath, target: PurePosixPath) -> str`
- Protocol enables type-safe strategy implementations without inheritance
- Allows users to provide custom rendering strategies for different deployment needs

**RelativePathStrategy Implementation**

- Implement as the default strategy for calculating relative paths
- Accept optional `site_prefix` parameter in `__init__` (e.g., `mysite/static`)
- Use `PurePosixPath` for all path calculations to ensure cross-platform consistency
- Calculate relative path from target location to source PurePosixPath path
- If site_prefix is provided, prepend it to the calculated relative path
- Handle edge cases like same directory (./file.css), parent directories (../), and nested paths

**Tree Walking Helper**

- Extract the tree-walking pattern from `make_path_nodes()` into a reusable helper function
- Name the helper `_walk_tree(node: Node, transform_fn: Callable[[Node], Node]) -> Node`
- Helper should accept a node and a transformation function
- Helper recursively walks the tree applying the transformation function
- Maintains immutability by creating new nodes only when changes occur
- Returns same object reference when no transformations are applied (optimization)
- Refactor `make_path_nodes()` to use this new helper internally

**Immutability and Optimization**

- All transformations create new Node instances (preserve immutability)
- When a node requires no changes, return the original object reference
- Only create new parent nodes when at least one child has changed
- This optimization reduces memory allocation and allows identity checks

## Visual Design

No visual assets provided for this feature.

## Existing Code to Leverage

**Tree Walking Pattern in `make_path_nodes()`**

- Located in `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py` lines 154-189
- Contains recursive `walk()` function that traverses Node trees using pattern matching
- Handles Element, Fragment, Text, and Comment nodes appropriately
- Implements optimization to return same object when children unchanged
- Should be extracted into `_walk_tree()` helper and reused by both functions

**PathElement Class**

- Located in `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py` lines 24-58
- Already defined and tested as Element subclass with PurePosixPath attribute support
- Used to preserve type information for component asset paths through rendering pipeline
- Attributes accept `str | PurePosixPath | None` values
- Detection logic: `isinstance(node, PathElement)`

**Path Utilities in `webpath.py`**

- Located in `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/webpath.py`
- `make_path()` function returns PurePosixPath instances from component and asset path
- PurePosixPath instances have `__str__()` and `__fspath__()` methods for string conversion
- These paths can be used with `PurePosixPath` for relative path calculations

**Element and Node Types from tdom**

- Element, Fragment, Text, Comment, and Node types from `tdom` package
- Pattern matching on node types (Element, Fragment, etc.) used throughout tree walking
- Element has tag, attrs, and children properties
- Creating new Elements preserves immutability while allowing transformations

**Optimization Pattern for Unchanged Nodes**

- Located in `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py` lines 169-174
- Checks `if any(new is not old for new, old in zip(new_children, children))`
- Only creates new node if children identity has changed
- This pattern should be preserved in `_walk_tree()` helper and used by `render_path_nodes()`

## Out of Scope

- HTML serialization to string output (separate concern handled by tdom)
- CSS or JavaScript bundling and optimization (build tool responsibility)
- Multi-page rendering coordination or site generation logic (SSG framework responsibility)
- Asset copying or file system operations (build system responsibility)
- Absolute URL generation with domain names (requires additional context)
- Caching of path calculations across multiple render calls (optimization for later)
- Validation that target paths exist on filesystem (error handling for later)
- Integration with specific web frameworks (Flask, Django, etc.)
- Custom path resolution beyond relative paths (extensible via strategy but not built-in)
- Handling of non-PurePosixPath path types beyond strings (current scope limited to PurePosixPath)

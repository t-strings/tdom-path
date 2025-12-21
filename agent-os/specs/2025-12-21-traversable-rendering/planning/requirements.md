# Spec Requirements: Path Rendering

## Initial Description

This feature involves writing a function that walks the tree looking for `TraversableElement` and rewrites values into
`Element` with paths relative to the target. This is the next planned feature according to the project roadmap (item
#3).

## Requirements Discussion

### First Round Questions

**Q1:** Function Name & API - I'm assuming we'll create a function named `render_path_nodes()` that takes the tree and
target path. Should it be:
`render_path_nodes(tree: Node, target: PurePath, strategy: RenderStrategy = RelativePathStrategy())` or would you prefer
a different name/signature?

**Answer:** Yes - use
`render_path_nodes(tree: Node, target: PurePath, strategy: RenderStrategy = RelativePathStrategy())`

**Q2:** TraversableElement Detection - I assume we'll detect `TraversableElement` using
`isinstance(node, TraversableElement)` and then inspect its attributes for `PurePosixPath` values. Should we also check
specific attribute names (like `href`, `src`) or scan all attributes?

**Answer:** Yes - detect using `isinstance(node, TraversableElement)` and inspect attributes for `PurePosixPath` values

**Q3:** Rendering Strategy Pattern - I'm thinking we should use a Protocol-based strategy pattern where
`RelativePathStrategy` is the default but users can provide custom strategies. Should the strategy have a method like
`calculate_path(source: PurePosixPath, target: PurePath) -> str`?

**Answer:** Yes - Protocol-based strategy pattern with default `RelativePathStrategy`, but consider using
`PurePosixPath` instead of `PurePath`

**Q4:** Output Element Type - I assume the function returns a tree where `TraversableElement` nodes are replaced with
regular `Element` instances containing string `href`/`src` attributes. Is that correct, or should we keep them as
`TraversableElement` but with string attributes?

**Answer:** Yes - create regular `Element` instances (not `TraversableElement`) with string href/src attributes

**Q5:** Refactoring Helpers - Since we already have tree-walking code in the asset rewriting, should we refactor out a
shared `_walk_tree(node, transform_fn)` helper, or keep this implementation separate for now?

**Answer:** Yes - extract walking pattern into reusable helper like `_walk_tree(node, transform_fn)`

**Q6:** Site Prefix Support - Should we support an optional site prefix (e.g., `/static/`) in the `RelativePathStrategy`
for cases where assets are served from a subdirectory? Or keep it pure relative paths only?

**Answer:** Include it in `RelativePathStrategy` with optional parameter, provide examples using `mysite/static` as the
prefix

**Q7:** Immutability & Optimization - I assume we should maintain immutability (return new nodes) but optimize to return
the same object reference when no changes are needed. Should we also cache path calculations within a single render
call?

**Answer:** Yes - preserve immutability, return same object reference when no changes occur

**Q8:** What should we NOT include in this spec? For example: HTML serialization, CSS/JS bundling, multi-page rendering,
or any other features that might seem related but should be separate?

**Answer:** Skip this question (no explicit exclusions)

### Existing Code to Reference

No similar existing features identified for reference.

### Follow-up Questions

None required.

## Visual Assets

### Files Provided:

No visual assets provided.

### Visual Insights:

Not applicable.

## Requirements Summary

### Functional Requirements

- Create a `render_path_nodes()` function that walks the tree and transforms `TraversableElement` nodes
- Function signature:
  `render_path_nodes(tree: Node, target: PurePath, strategy: RenderStrategy = RelativePathStrategy())`
- Detect `TraversableElement` instances using `isinstance()` checks
- Inspect all attributes of detected nodes for `PurePosixPath` values
- Transform detected `TraversableElement` nodes into regular `Element` nodes
- Replace `PurePosixPath` attribute values with string representations (relative paths)
- Use `PurePosixPath` instead of `PurePath` for path calculations
- Implement Protocol-based strategy pattern for path rendering
- Provide `RelativePathStrategy` as default strategy implementation
- Support optional site prefix parameter in `RelativePathStrategy` (e.g., `mysite/static`)
- Extract tree-walking pattern into reusable helper function `_walk_tree(node, transform_fn)`
- Maintain immutability in tree transformations
- Optimize to return same object reference when no transformations are needed
- Provide usage examples demonstrating site prefix with `mysite/static`

### Reusability Opportunities

- Existing tree-walking code in asset rewriting should be refactored into shared helper
- Tree traversal patterns from existing codebase can inform implementation
- Strategy pattern approach allows future extension for different rendering needs

### Scope Boundaries

**In Scope:**

- Core `render_path_nodes()` function implementation
- `RenderStrategy` Protocol definition
- `RelativePathStrategy` implementation with site prefix support
- Refactored `_walk_tree()` helper function
- Detection and transformation of `TraversableElement` nodes
- Relative path calculation using `PurePosixPath`
- Immutability preservation with optimization for unchanged trees
- Examples demonstrating usage with site prefixes

**Out of Scope:**

- No explicit exclusions specified
- Presumably excludes HTML serialization (separate concern)
- Presumably excludes CSS/JS bundling (separate concern)
- Presumably excludes multi-page rendering coordination (separate concern)

### Technical Considerations

- Use `PurePosixPath` instead of `PurePath` for cross-platform path consistency
- Strategy pattern enables extensibility for future rendering needs
- Immutability must be preserved while optimizing for no-change scenarios
- Tree-walking helper should be generic enough for reuse in other tree operations
- Site prefix feature requires careful path joining to avoid double slashes or incorrect paths
- Protocol-based design allows type-safe strategy implementations

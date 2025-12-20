# Spec Requirements: Core Path API

## Initial Description

Implement `PurePath`-compatible path classes that represent component-relative paths, support basic path operations (
join, resolve, relative), and provide type hints for IDE integration. Include unit tests covering path arithmetic, edge
cases, and cross-platform compatibility.

This is Phase 1 from the product roadmap.

### Context from Raw Idea

- This is part of the `tdom-path` library which rewrites paths (static assets, links) in a `Node` to be relative to a
  target
- The goal is to provide great DX via actual paths that work with IDE tooling (autocomplete, refactoring, squiggles)
- Must be framework-portable (not tied to Flask, Django, etc.)
- Should use PurePath interface for tooling compatibility
- Needs to support both dynamic servers and SSG (static site generators)

## Requirements Discussion

### First Round Questions

**Q1:** For the path classes, should we use `Path` (actual filesystem) or `PurePath` (virtual paths)? I'm assuming we
need `PurePath` for web-style virtual paths (like `/blog/post.html`) that don't necessarily exist on disk, but should we
also support `Path` for actual filesystem operations (reading component files, validating assets exist)?

**Answer:** Use `Path` (not `PurePath`) for actual filesystem paths. Don't need to implement `resolve()` etc. since
`Path` provides them. BUT also keep `PurePosixPath` semantics for web-style virtual paths.

**Q2:** The component-relative path pattern seems to involve storing paths relative to some "site root", then computing
dotted relative paths (like `../../static/styles.css`) when rendering. Should we follow the pattern in the existing
tdom-sphinx implementation, or do you want a different approach?

**Answer:** Reference implementation at `../tdom-sphinx/src/tdom_sphinx/url.py` shows the pattern - paths stored
relative to site root, then compute dotted relative paths when rendering. Stay close to `pathlib` API idioms (override
`relative_to()` if needed). Rethink/redesign the logic (don't just copy).

**Q3:** For cross-platform compatibility, I'm thinking we should use `PurePosixPath` as the primary interface (for web
URLs which are always POSIX-style), but ensure the implementation works on Windows for development environments. Should
we have separate classes for filesystem paths vs. web paths, or a single unified interface?

**Answer:** Use `PurePosixPath` as primary (web URLs), but ensure Windows cross-platform compatibility with testing.

**Q4:** Path validation - should we fail fast when a component's markup points to a non-existent path, or defer
validation until render/build time? I'm assuming we should validate early (at construction/resolution time) to catch
errors quickly, but should this be configurable?

**Answer:** Fail quickly when component markup points to non-existent paths. Validate at construction/resolution time.

**Q5:** For type hints, should we aim for strict mypy compliance with no `type: ignore` comments, or is "good enough"
strictness acceptable? Should we use Protocols for extensibility points?

**Answer:** Good strictness (not perfect). Protocol is acceptable if needed.

**Q6:** What edge cases should the tests cover beyond basic path arithmetic? I'm thinking:

- Paths with `#` anchors (like `/page.html#section`)
- Handling `some_folder/` vs `some_folder/index.html` equivalence
- Root paths and relative-to calculations
- Empty path segments, special characters, deeply nested paths

Are there other edge cases from your experience with the existing implementations?

**Answer:** Edge cases to cover:

- `#` internal anchors in URLs
- `some_folder/` vs `some_folder/index.html` equivalence (HTML URL quirk)
- Root paths, common parents, `..` hops, static prefixes (from existing implementation)
- Same source/target optimization
- Empty path segments, special characters, deep nesting

**Q7:** Since this is Phase 1 and will later integrate with Node annotations (Phase 2) and context objects (Phase 3),
should we design the API with those future features in mind, or keep it completely standalone for now?

**Answer:** Design API anticipating Node redesign in Phase 2 (though not implementing annotations yet).

**Q8:** For testing, should we use pytest with specific plugins (pytest-cov, pytest-xdist for parallel execution), and
should we include Windows-specific test runs in CI? What's your coverage target - 100% or is 90%+ acceptable?

**Answer:** pytest with 100% coverage goal, Windows cross-platform testing, reference tdom-sphinx tests for ideas.

**Q9:** Are there any features from the roadmap that are explicitly OUT of scope for Phase 1? For example, should we NOT
implement context objects, site prefixes, or Node integration in this phase?

**Answer:** Scope exclusions for Phase 1:

- NO context objects (Phase 3)
- NO Node annotations implementation (Phase 2 - though anticipate the design)
- NO tree rewriting/middleware (Phase 4)
- NO site prefix support (Phase 6)
- NO framework integrations (Phases 11-12)

### Existing Code to Reference

**Similar Features Identified:**

- **Feature:** tdom-sphinx URL handling - Path: `../tdom-sphinx/src/tdom_sphinx/url.py`
- **Components to potentially reference:**
    - `relative_path()` function: Core algorithm for calculating dotted relative paths from source to destination
    - `normalize()` function: Converting various inputs to `PurePosixPath`
    - `relative()` function: High-level API with policies for static assets vs. document links
    - Pattern: Paths stored relative to site root with leading `/`, then compute `..` hops at render time
    - Optimization: Bail out early if source == target
    - Edge case handling: ROOT paths, static_prefix logic, suffix handling
- **Backend logic to reference:**
    - Path validation requiring absolute paths (leading `/`)
    - Algorithm: Iterate through parents to find common ancestor, calculate hops, build relative path
    - Static prefix injection between dots and target

**Important constraint:** Rethink/redesign the logic rather than copying it directly. Stay close to `pathlib` API
idioms.

**Other codebases:** Don't look at other implementations (2019 version, tdom branch, etc.) - focus on clean redesign.

### Follow-up Questions

None required - all critical requirements clarified in first round.

## Visual Assets

### Files Provided:

No visual assets provided.

### Visual Insights:

N/A - This is a library API with no visual interface.

## Requirements Summary

### Functional Requirements

**Core Path Classes:**

- Implement path classes compatible with `PurePath` interface for IDE tooling support
- Use `Path` for actual filesystem paths (component source files, asset validation)
- Use `PurePosixPath` for web-style virtual paths (URLs, links)
- Support component-relative path storage (paths relative to site root with leading `/`)
- Compute dotted relative paths (`../../target`) at resolution time

**Path Operations:**

- `join`: Combine path segments following POSIX path rules
- `resolve`: Normalize paths, eliminate `.` and `..` segments (leveraging `Path` built-ins where appropriate)
- `relative_to()`: Calculate relative path from source to target with `..` hops
- Support both absolute (from root) and relative path representations

**Path Validation:**

- Fail fast when paths point to non-existent resources
- Validate at construction/resolution time (not deferred to render time)
- Provide clear error messages indicating what path failed and why

**Type Hints:**

- Good strictness level (not perfectionist)
- Use Protocols where needed for extensibility
- Enable IDE autocomplete, go-to-definition, type checking
- Support mypy/pyright static analysis

**Path Resolution Algorithm:**

- Start with paths stored relative to site root (absolute with leading `/`)
- Find common ancestor between source and target paths
- Calculate number of `..` hops needed to reach common ancestor
- Build relative path: `..` hops + remainder from common ancestor to target
- Optimize: If source == target, return just the filename
- Support static prefix injection between hops and target (for asset directories)

### Edge Cases to Handle

**URL-Specific:**

- Internal anchors: `/page.html#section` should preserve anchor
- Folder vs. index equivalence: `/blog/` and `/blog/index.html` should be treated consistently
- Root path handling: `/` should normalize to `/index`

**Path Arithmetic:**

- Common parent detection: Handle arbitrary nesting levels
- Same source/target: Optimize to return just filename
- Root-level paths: Handle paths at site root without parent
- Deep nesting: Support arbitrarily deep directory hierarchies

**Special Characters & Segments:**

- Empty path segments: Normalize away (e.g., `/blog//post/` → `/blog/post`)
- Special characters: URL encoding, spaces, unicode
- Dot segments: Proper handling of `.` and `..` in paths

**Cross-Platform:**

- Windows path separators: Ensure `PurePosixPath` works correctly on Windows
- Case sensitivity: Consider case-insensitive filesystems
- Path length limits: Windows MAX_PATH considerations

**Static Prefix Handling:**

- Insert static prefix between `..` hops and target path
- Support optional prefix (None means no prefix)
- Example: `../../_static/styles.css` with prefix `_static`

### Reusability Opportunities

**Patterns from tdom-sphinx/url.py:**

- Algorithm for finding common parent and calculating hops
- Optimization pattern for same source/target
- Normalization patterns for various input types
- Static prefix injection strategy
- ROOT path constants and handling

**Do NOT reuse directly:**

- Don't copy the implementation - rethink and redesign
- Stay closer to `pathlib` API idioms
- Consider overriding `relative_to()` method rather than separate functions
- Simplify where possible

**Future integration points to anticipate:**

- Node annotation storage (Phase 2): Paths should be serializable/storable
- Context object pattern (Phase 3): Path resolution will receive context
- Path rewriting (Phase 4): Bulk operations on path collections
- Site prefix support (Phase 6): Architecture should allow prefix configuration

### Scope Boundaries

**In Scope (Phase 1):**

- `PurePath`-compatible path classes
- `Path` for filesystem operations
- `PurePosixPath` for web virtual paths
- Component-relative path representation
- Basic path operations: join, resolve, relative_to
- Path validation with fast failure
- Type hints for IDE integration
- Comprehensive unit tests (100% coverage goal)
- Cross-platform compatibility (Windows testing)
- Edge case handling (anchors, root paths, special chars)

**Out of Scope (Future Phases):**

- Context objects (Phase 3) - though API should anticipate them
- Node annotations implementation (Phase 2) - though API should anticipate them
- Tree rewriting/middleware (Phase 4)
- Site prefix support (Phase 6) - though architecture should allow it
- Framework integrations (Phases 11-12)
- Static asset path rewriting (Phase 4)
- Link path rewriting (Phase 5)
- Build-time asset collection (Phase 9)
- Performance optimizations/caching (Phase 13)

**Design Anticipation (Don't Implement Yet):**

- Node annotation storage format
- Context object interface
- Site prefix configuration pattern
- Path resolver protocol

### Technical Considerations

**Technology Stack:**

- Python 3.14+ (free-threaded support targeted)
- `pathlib.Path` and `pathlib.PurePosixPath` from standard library
- `typing.Protocol` for extensibility
- pytest for testing framework
- mypy or pyright for type checking

**Path Class Design:**

- Inherit from or wrap `PurePosixPath` for web paths
- Use `Path` directly for filesystem operations
- Override `relative_to()` to implement dotted relative path logic
- Maintain `pathlib` API compatibility for IDE support

**Algorithm Reference (from tdom-sphinx):**

```python
# Conceptual approach (redesign, don't copy):
1.
Validate
both
paths
are
absolute(start
with / )
2.
Optimization:
if source == target, return filename only
3.
Iterate
through
source
parents
to
find
common
ancestor
with target
    4.
Count
hops
from source to

common
ancestor
5.
Calculate
remainder
from common ancestor

to
target
6.
Build
result: '../' * hops + [optional static_prefix] + remainder
```

**Validation Strategy:**

- Check at construction time if path exists (for filesystem paths)
- Check at resolution time if target is valid
- Raise clear exceptions with path information
- Design for helpful error messages

**Testing Strategy:**

- Unit tests for each path operation
- Edge case tests for all identified scenarios
- Cross-platform tests (Windows, Unix)
- Reference tdom-sphinx tests for pattern ideas
- Aim for 100% code coverage
- Use pytest fixtures for common test paths

**Cross-Platform Requirements:**

- Primary interface uses POSIX paths (for web URLs)
- Ensure tests pass on Windows
- Use `PurePosixPath` to avoid platform-specific separators
- Test with Windows paths where filesystem interaction occurs

**Performance Considerations (for future):**

- Algorithm should be efficient (avoid redundant calculations)
- Same source/target optimization is important
- Design with caching in mind (Phase 13) though don't implement yet
- Consider free-threaded Python compatibility in design

**Type Safety:**

- Comprehensive type hints on all public APIs
- Use `Protocol` for extensibility points
- Enable strict mypy/pyright checking
- Support IDE features: autocomplete, type checking, refactoring

**Documentation Needs:**

- Docstrings on all public classes/methods
- Algorithm explanation for relative path calculation
- Edge case handling documentation
- Examples of usage patterns
- Type annotations as inline documentation

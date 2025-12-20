# Specification: Core Path API

## Goal

Create a pathlib-compatible path API that enables component-relative path calculations for web URLs, supporting both
filesystem validation and virtual web paths with IDE tooling integration and cross-platform compatibility.

## User Stories

- As a theme developer, I want to write `./static/styles.css` in my component markup and have it automatically resolve
  to the correct relative path (`../../static/styles.css`) when rendered at different URLs
- As a component author, I want IDE autocomplete, go-to-definition, and refactoring support for asset paths so I can
  catch broken references during development rather than at runtime
- As a site builder, I want errors and warnings about missing resources at paths.

## Specific Requirements

**PurePosixPath-based Web Path Class**

- Inherit from or wrap `PurePosixPath` to represent web URLs (always POSIX-style with `/` separators)
- Store paths as actual filesystem paths to component assets (e.g., `src/mysite/components/heading/static/heading.css`)
  rather than web URL paths
- Support standard pathlib operations: `joinpath()`, `with_suffix()`, `name`, `parent`, `parents`
- Override `relative_to()` method to calculate dotted relative paths with `..` hops (e.g., `../../target`) for web
  output
- Maintain type compatibility with `PurePosixPath` for IDE tooling and mypy/pyright type checking

**Filesystem Path Support**

- Use standard library `Path` class for actual filesystem operations (reading component files, validating assets exist)
- Leverage built-in `Path.resolve()`, `Path.exists()`, and other filesystem methods without reimplementation
- Support cross-platform filesystem paths while maintaining POSIX semantics for web URL output
- Design for Windows compatibility where filesystem paths use backslashes but web URLs use forward slashes

**Relative Path Calculation Algorithm**

- Accept component-relative paths (e.g., `static/style.css`, `./static/style.css`) from component markup
- Resolve component-relative paths to absolute filesystem paths based on component location
- Calculate web-relative paths between a current render location and a target asset location
- Optimize same source/target case: return just the filename when source == target
- Find common ancestor by iterating through source path parents until match found in target parents
- Count hops (`..` segments) needed from source to common ancestor
- Calculate remainder path from common ancestor to target
- Build result: `../` repeated for each hop + remainder path

**Path Validation and Error Handling**

- Validate that component-relative paths can be resolved to actual filesystem locations
- Raise clear errors with descriptive messages when paths are invalid or malformed
- Fail fast when component markup references non-existent filesystem paths
- Include both the component-relative path and resolved filesystem path in error messages for easier debugging
- Handle edge cases: missing leading `./`, parent directory references (`../`), absolute paths in component markup

**Edge Case Handling: URL Anchors**

- Preserve internal anchors in URLs (e.g., `page.html#section` should keep `#section`)
- Split anchor from path before relative calculation, then reattach to result
- Handle edge cases: `#section` alone (pure anchor), empty anchors, multiple `#` characters

**Edge Case Handling: Folder vs Index Equivalence**

- Treat `blog/` and `blog/index.html` as semantically equivalent for path resolution
- Normalize folder paths to include `index` when needed for common ancestor calculation
- Handle root-level index: root folder should normalize to `index` for consistent behavior
- Provide clear policy on when to add/remove `index` suffix

**Edge Case Handling: Path Arithmetic**

- Support component-relative paths at any depth (e.g., `static/style.css`, `images/logo.png`, `js/utils/helper.js`)
- Handle deeply nested component structures (arbitrary directory depth) efficiently
- Normalize empty path segments and redundant separators
- Handle special characters in paths: spaces, unicode characters
- Process `.` and `..` segments correctly during path normalization and resolution

**Type Hints and IDE Integration**

- Use comprehensive type hints on all public classes, methods, and functions
- Define Protocol interfaces for extensibility points (anticipating future context objects and resolvers)
- Support mypy and pyright static type checking with good strictness (not perfectionist)
- Enable IDE features: autocomplete on path methods, go-to-definition for path classes, type inference for path
  operations

**Future-Ready Design for Node Integration**

- Design path classes to be serializable/storable in Node annotations (Phase 2)
- Anticipate paths being passed through context objects (Phase 3) without implementing context yet
- Consider how paths will be collected for bulk rewriting operations (Phase 4)
- Allow for site prefix configuration architecture (Phase 6) without implementing it now

**Testing Strategy with 100% Coverage**

- Unit tests for each path operation: join, resolve, relative_to, normalization
- Edge case tests: anchors, root paths, same source/target, empty segments, special characters, deep nesting
- Cross-platform tests: run full test suite on Windows and Unix systems
- Reference tdom-sphinx test patterns for algorithm validation
- Use pytest fixtures for common test path scenarios (root paths, nested paths, static assets)
- Parameterized tests for edge cases with multiple input variations

## Visual Design

No visual assets provided (library API).

## Existing Code to Leverage

**`tdom-sphinx/src/tdom_sphinx/url.py` - Core Algorithm Pattern**

- `relative_path()` function demonstrates the algorithm: find common ancestor, count hops, build dotted path
- Optimization pattern: bail out early if source == target, return just filename
- Validation pattern: require absolute paths with leading `/`, raise ValueError with clear messages
- Static prefix injection: insert prefix path between `..` hops and target remainder
- Constants pattern: define ROOT as `PurePosixPath("/")` and ROOT_PATHS tuple for quick checks

**`tdom-sphinx/src/tdom_sphinx/url.py` - Normalization Pattern**

- `normalize()` function converts various input types (str, PurePosixPath) to standardized form
- Root path normalization: `/`, `/index`, and variants all normalize to `PurePosixPath("/index")`
- Type checking pattern: use `isinstance()` to handle multiple input types gracefully
- Clear error messages for unsupported input types

**`tdom-sphinx/src/tdom_sphinx/url.py` - High-Level API Pattern**

- `relative()` function wraps low-level algorithm with policy decisions
- Handles suffix addition (e.g., `.html`) for document links
- Handles static prefix for asset paths vs. document paths
- Pattern of normalize-inputs -> calculate-path -> apply-suffix demonstrates layered design

**`tdom-sphinx/src/tdom_sphinx/url.py` - Parent Iteration Algorithm**

- Use `iter(current.parents)` to walk up directory tree
- Check if each parent is `in target.parents` to find common ancestor
- Count iterations as hop count for `..` segments
- Use `target.relative_to(result)` to extract remainder path after common ancestor

**Important Constraint: Rethink, Don't Copy**

- Redesign the logic to be more pathlib-idiomatic (override `relative_to()` rather than separate functions)
- Simplify where possible while maintaining edge case handling
- Stay closer to standard pathlib API patterns for better IDE integration
- Consider what can be eliminated or consolidated from the reference implementation

## Out of Scope

- Context objects implementation (Phase 3 - design should anticipate but not implement)
- Node annotations implementation (Phase 2 - design should anticipate but not implement)
- Tree rewriting and middleware patterns (Phase 4)
- Site prefix configuration and support (Phase 6 - architecture should allow but not implement)
- Framework integrations for Flask, Django, FastAPI, Sphinx, Pelican (Phases 11-12)
- Static asset path rewriting in actual Node trees (Phase 4)
- Link path rewriting in markup (Phase 5)
- Build-time asset collection and optimization (Phase 9)
- Performance optimizations, caching, or memoization (Phase 13)
- Convention-based asset discovery (automatic `static/` directory scanning)
- URL-to-filesystem path mapping for dynamic servers (Flask routes, Django URLs)

# Task Breakdown: Core Path API

## Overview

Total Task Groups: 6
Focus: Library API for pathlib-compatible web path operations with IDE integration

## Task List

### Core Path Classes

#### Task Group 1: Path Class Foundation

**Dependencies:** None

- [ ] 1.0 Complete path class foundation
    - [ ] 1.1 Write 2-8 focused tests for WebPath basic operations
        - Limit to 2-8 highly focused tests maximum
        - Test only critical path behaviors (construction, basic properties, POSIX semantics)
        - Skip exhaustive coverage of all pathlib methods
    - [ ] 1.2 Create WebPath class wrapping/inheriting PurePosixPath
        - Always use POSIX-style `/` separators (web URL semantics)
        - Store component filesystem paths as instance data
        - Implement basic pathlib-compatible properties: `name`, `suffix`, `parent`, `parents`
        - Support standard pathlib methods: `joinpath()`, `with_suffix()`
        - Reference pattern: `pathlib.PurePosixPath` for API compatibility
    - [ ] 1.3 Add type hints and Protocol definitions
        - Comprehensive type hints on all public APIs
        - Define `PathLike` Protocol for extensibility (anticipate future context objects)
        - Enable mypy/pyright strict checking (good strictness, not perfectionist)
        - Support IDE autocomplete and type inference
    - [ ] 1.4 Implement basic path validation
        - Validate paths conform to POSIX format
        - Check for malformed paths (e.g., multiple consecutive `/`, invalid characters)
        - Raise `ValueError` with clear messages indicating what failed
    - [ ] 1.5 Ensure path class foundation tests pass
        - Run ONLY the 2-8 tests written in 1.1
        - Verify basic pathlib operations work
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 1.1 pass
- WebPath compatible with PurePosixPath API
- Type hints enable IDE autocomplete and go-to-definition
- Basic validation catches malformed paths

### Path Resolution and Calculation

#### Task Group 2: Relative Path Algorithm

**Dependencies:** Task Group 1

- [ ] 2.0 Complete relative path calculation algorithm
    - [ ] 2.1 Write 2-8 focused tests for relative_to() override
        - Limit to 2-8 highly focused tests maximum
        - Test only critical relative path scenarios (basic relative, common ancestor, hop counting)
        - Skip exhaustive edge case testing (covered in Task Group 4)
    - [ ] 2.2 Override relative_to() method for dotted relative paths
        - Accept source and target paths (both absolute with leading `/`)
        - Calculate common ancestor by iterating through source.parents
        - Count hops (`..` segments) from source to common ancestor
        - Build remainder path from common ancestor to target
        - Return `PurePosixPath` with `../` repeated + remainder
        - Reference pattern: `../tdom-sphinx/src/tdom_sphinx/url.py` lines 13-100 (redesign, don't copy)
    - [ ] 2.3 Implement same source/target optimization
        - Detect when source == target before iterating parents
        - Return just the filename (e.g., `page.html` instead of `../page.html`)
        - Log performance optimization for future caching strategy (Phase 13)
    - [ ] 2.4 Add path normalization logic
        - Normalize root paths: `/`, `/index`, `PurePosixPath("/")` all become `/index`
        - Handle folder vs index equivalence: `blog/` and `blog/index.html`
        - Remove empty path segments (e.g., `/blog//post/` becomes `/blog/post/`)
        - Process `.` and `..` segments correctly during normalization
        - Reference pattern: `../tdom-sphinx/src/tdom_sphinx/url.py` lines 103-138 (redesign for pathlib idioms)
    - [ ] 2.5 Implement parent iteration algorithm
        - Use `iter(source.parents)` to walk up directory tree
        - Check if each parent is `in target.parents` to find common ancestor
        - Track hop count during iteration
        - Use `target.relative_to(common_ancestor)` to extract remainder
        - Handle edge case: root level paths with no parent
    - [ ] 2.6 Ensure relative path algorithm tests pass
        - Run ONLY the 2-8 tests written in 2.1
        - Verify critical relative path calculations work
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 2.1 pass
- relative_to() correctly calculates dotted relative paths with `..` hops
- Same source/target optimization returns just filename
- Path normalization handles root paths and folder/index equivalence

### Filesystem Integration

#### Task Group 3: Path Validation and Filesystem Operations

**Dependencies:** Task Group 2

- [ ] 3.0 Complete filesystem integration
    - [ ] 3.1 Write 2-8 focused tests for filesystem path validation
        - Limit to 2-8 highly focused tests maximum
        - Test only critical validation behaviors (exists check, resolve, fail fast)
        - Skip exhaustive filesystem edge cases
    - [ ] 3.2 Create FilesystemPath class using Path
        - Use standard library `Path` for actual filesystem operations
        - Leverage built-in `Path.resolve()`, `Path.exists()` without reimplementation
        - Support cross-platform filesystem paths (Windows backslashes, Unix forward slashes)
        - Convert filesystem paths to web paths (always POSIX) for output
    - [ ] 3.3 Implement fail-fast validation
        - Validate component-relative paths at construction/resolution time
        - Check if resolved filesystem path exists using `Path.exists()`
        - Raise clear errors with both component-relative and resolved filesystem paths
        - Example error: "Path './static/missing.css' resolves to '/path/to/component/static/missing.css' which does not
          exist"
    - [ ] 3.4 Add component-relative path resolution
        - Accept component-relative paths: `static/style.css`, `./static/style.css`
        - Resolve to absolute filesystem paths based on component location
        - Handle missing leading `./` (normalize `static/style.css` to `./static/style.css`)
        - Handle parent directory references (`../shared/base.css`)
        - Warn on absolute paths in component markup (anti-pattern)
    - [ ] 3.5 Design for cross-platform compatibility
        - Ensure `PurePosixPath` works correctly on Windows
        - Test with Windows filesystem paths (backslashes)
        - Verify web URL output always uses forward slashes
        - Document platform-specific behavior in docstrings
    - [ ] 3.6 Ensure filesystem integration tests pass
        - Run ONLY the 2-8 tests written in 3.1
        - Verify filesystem validation works
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 3.1 pass
- FilesystemPath uses standard library Path without reimplementation
- Fail-fast validation catches non-existent paths at construction time
- Component-relative paths resolve correctly to filesystem locations
- Cross-platform compatibility maintained (POSIX output, platform-agnostic input)

### Edge Case Handling

#### Task Group 4: URL Anchors and Special Cases

**Dependencies:** Task Group 2, Task Group 3

- [ ] 4.0 Complete edge case handling
    - [ ] 4.1 Write 2-8 focused tests for edge cases
        - Limit to 2-8 highly focused tests maximum
        - Test only critical edge cases (anchors, empty segments, special characters)
        - Skip exhaustive edge case combinations (covered in Task Group 6)
    - [ ] 4.2 Implement URL anchor preservation
        - Split anchor from path before relative calculation: `page.html#section` becomes `page.html` + `#section`
        - Calculate relative path for the non-anchor portion
        - Reattach anchor to result: `../../page.html` + `#section` becomes `../../page.html#section`
        - Handle pure anchor: `#section` (no path component)
        - Handle empty anchors: `page.html#` (anchor separator but no content)
        - Handle multiple `#` characters: `page.html#section#subsection` (use first as split point)
    - [ ] 4.3 Implement folder/index equivalence
        - Treat `blog/` and `blog/index.html` as semantically equivalent
        - Normalize folder paths to include `index` when calculating common ancestor
        - Handle root-level index: `/` becomes `/index` for consistency
        - Provide clear policy: when rendering links, add/remove `index` based on configuration (anticipate Phase 6)
    - [ ] 4.4 Handle special characters in paths
        - Support spaces in paths: `my file.html` (properly encoded in URLs)
        - Support unicode characters: `café.html`, `日本語.html`
        - Normalize redundant separators: `/blog//post///` becomes `/blog/post/`
        - Handle edge case: empty path segments between separators
    - [ ] 4.5 Handle deeply nested paths
        - Support arbitrary directory depth (no hardcoded limits)
        - Test with realistic nesting: `docs/guides/advanced/patterns/component-design/index.html`
        - Ensure algorithm efficiency doesn't degrade with depth
        - Verify hop counting works correctly for deep hierarchies
    - [ ] 4.6 Ensure edge case handling tests pass
        - Run ONLY the 2-8 tests written in 4.1
        - Verify critical edge cases work
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 4.1 pass
- URL anchors preserved through relative path calculation
- Folder/index equivalence handled consistently
- Special characters (spaces, unicode) supported
- Deeply nested paths work efficiently

### Future-Ready Design

#### Task Group 5: Protocol Definitions and Extension Points

**Dependencies:** Task Group 1, Task Group 2

- [ ] 5.0 Complete future-ready design
    - [ ] 5.1 Write 2-8 focused tests for Protocol compliance
        - Limit to 2-8 highly focused tests maximum
        - Test only critical Protocol behaviors (interface compliance, type checking)
        - Skip testing future implementations (context objects, Node integration)
    - [ ] 5.2 Define PathResolver Protocol
        - Define interface for path resolution strategies
        - Anticipate context objects (Phase 3) without implementing
        - Methods: `resolve(path: str) -> WebPath`, `validate(path: str) -> bool`
        - Support dependency injection pattern for testing and extensibility
    - [ ] 5.3 Design for Node annotation storage (Phase 2)
        - Ensure WebPath is serializable (can be stored in annotations)
        - Consider JSON representation for Node tree storage
        - Document anticipated annotation format in docstrings
        - Do NOT implement Node class or annotation system yet
    - [ ] 5.4 Design for site prefix support (Phase 6)
        - Add `static_prefix` parameter to relative_to() signature (optional)
        - Insert prefix between `..` hops and remainder path
        - Example: `../../_static/styles.css` with prefix `_static`
        - Document prefix injection strategy in docstrings
        - Do NOT implement configuration system yet
    - [ ] 5.5 Add extensibility documentation
        - Document Protocol interfaces for future implementers
        - Explain how to extend WebPath for custom path types
        - Provide examples of anticipated future usage (context objects, Node integration)
        - Reference Phase 2-6 roadmap in module docstring
    - [ ] 5.6 Ensure Protocol tests pass
        - Run ONLY the 2-8 tests written in 5.1
        - Verify Protocol compliance
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 5.1 pass
- PathResolver Protocol defined with clear interface
- WebPath designed for Node annotation storage (serializable)
- Site prefix architecture allows future configuration (Phase 6)
- Documentation explains extension points and future integration

### Comprehensive Testing and Cross-Platform Validation

#### Task Group 6: Test Coverage and Cross-Platform Compatibility

**Dependencies:** Task Groups 1-5

- [ ] 6.0 Complete comprehensive testing and validation
    - [ ] 6.1 Review existing tests from Task Groups 1-5
        - Review the 2-8 tests written by path-foundation engineer (Task 1.1)
        - Review the 2-8 tests written by algorithm engineer (Task 2.1)
        - Review the 2-8 tests written by filesystem engineer (Task 3.1)
        - Review the 2-8 tests written by edge-case engineer (Task 4.1)
        - Review the 2-8 tests written by protocol engineer (Task 5.1)
        - Total existing tests: approximately 10-40 tests
    - [ ] 6.2 Analyze test coverage gaps for Core Path API only
        - Identify critical path operation workflows lacking coverage
        - Focus ONLY on gaps related to this spec's requirements
        - Do NOT assess entire application test coverage
        - Prioritize integration tests combining multiple path operations
        - Reference `../tdom-sphinx/tests/` for test pattern ideas
    - [ ] 6.3 Write up to 10 additional strategic tests maximum
        - Add maximum of 10 new tests to fill identified critical gaps
        - Focus on integration scenarios: full path resolution + validation + relative calculation
        - Test cross-platform behavior: Windows path input, POSIX path output
        - Test algorithm edge cases: root paths, same source/target, deep nesting, anchors combined
        - Do NOT write comprehensive coverage for all scenarios
        - Skip performance tests (Phase 13), skip framework integration tests (Phases 11-12)
    - [ ] 6.4 Set up cross-platform test infrastructure
        - Configure pytest for Windows and Unix test runs
        - Use pytest fixtures for common test paths (root, nested, static assets)
        - Parameterize tests for platform-specific behavior
        - Document how to run tests on Windows in test docstrings
    - [ ] 6.5 Create pytest fixtures for common scenarios
        - Fixture: `root_path` - paths at site root (`/`, `/index`)
        - Fixture: `nested_path` - deeply nested paths (`/docs/guides/advanced/index.html`)
        - Fixture: `static_asset` - component-relative asset paths (`./static/styles.css`)
        - Fixture: `anchor_path` - paths with URL anchors (`page.html#section`)
        - Fixture: `temp_filesystem` - temporary directory structure for validation tests
    - [ ] 6.6 Implement parameterized tests for edge cases
        - Parameterize anchor tests: pure anchor, empty anchor, multiple `#`
        - Parameterize special character tests: spaces, unicode, encoded characters
        - Parameterize normalization tests: folder/index equivalence, empty segments, dot segments
        - Use `pytest.mark.parametrize` for readable test matrix
    - [ ] 6.7 Add cross-platform specific tests
        - Test Windows filesystem paths with backslashes
        - Test case-insensitive filesystem behavior (Windows, macOS)
        - Test path length limits (Windows MAX_PATH)
        - Verify POSIX output on all platforms
    - [ ] 6.8 Verify 100% test coverage goal
        - Run pytest with coverage plugin: `pytest --cov=tdom_path --cov-report=term-missing`
        - Identify any untested code paths
        - Add focused tests for uncovered lines (within 10 test budget)
        - Document any intentional coverage exclusions (e.g., defensive error handling)
    - [ ] 6.9 Run feature-specific tests only
        - Run ONLY tests related to Core Path API (tests from 1.1, 2.1, 3.1, 4.1, 5.1, and 6.3)
        - Expected total: approximately 20-50 tests maximum
        - Do NOT run tests for future phases (context objects, Node integration, framework integrations)
        - Verify critical workflows pass: component-relative resolution, relative path calculation, filesystem
          validation
    - [ ] 6.10 Document testing strategy and patterns
        - Add module docstring explaining test organization
        - Document how to run tests on different platforms
        - Explain parameterization strategy for edge cases
        - Reference tdom-sphinx test patterns used

**Acceptance Criteria:**

- All feature-specific tests pass (approximately 20-50 tests total)
- Test coverage at or near 100% (with documented exclusions)
- No more than 10 additional tests added when filling in testing gaps
- Cross-platform tests pass on Windows and Unix
- Testing focused exclusively on Core Path API requirements (Phase 1)
- pytest fixtures provide reusable test scenarios

## Execution Order

Recommended implementation sequence:

1. Core Path Classes (Task Group 1) - Foundation for all path operations
2. Path Resolution and Calculation (Task Group 2) - Core algorithm implementation
3. Filesystem Integration (Task Group 3) - Validation and cross-platform support
4. Edge Case Handling (Task Group 4) - URL anchors, special characters, folder/index equivalence
5. Future-Ready Design (Task Group 5) - Protocols and extension points for Phase 2-6
6. Comprehensive Testing (Task Group 6) - Test coverage, cross-platform validation, gap analysis

## Important Constraints

- **Rethink, don't copy**: Reference `tdom-sphinx/url.py` for algorithm patterns, but redesign for pathlib idioms
- **Stay close to pathlib API**: Override `relative_to()` method rather than creating separate functions
- **Cross-platform compatibility**: Use `PurePosixPath` for web semantics, support Windows filesystem paths
- **Fail fast**: Validate paths at construction/resolution time, not deferred to render time
- **Type safety**: Comprehensive type hints, Protocol definitions, IDE integration support
- **Future-ready**: Anticipate Node annotations (Phase 2) and context objects (Phase 3) without implementing
- **Testing focus**: 100% coverage goal, cross-platform tests, reference tdom-sphinx test patterns
- **Scope discipline**: Do NOT implement context objects, Node integration, site prefix configuration, or framework
  integrations

## Out of Scope (Future Phases)

- Context objects (Phase 3)
- Node annotations implementation (Phase 2)
- Tree rewriting and middleware (Phase 4)
- Site prefix configuration (Phase 6)
- Framework integrations (Phases 11-12)
- Static asset path rewriting in Node trees (Phase 4)
- Link path rewriting in markup (Phase 5)
- Build-time asset collection (Phase 9)
- Performance optimizations and caching (Phase 13)

## Reference Code

- Algorithm pattern: `/Users/pauleveritt/projects/t-strings/tdom-path/../tdom-sphinx/src/tdom_sphinx/url.py` (lines
  13-100)
- Normalization pattern: `/Users/pauleveritt/projects/t-strings/tdom-path/../tdom-sphinx/src/tdom_sphinx/url.py` (lines
  103-138)
- Test patterns: `../tdom-sphinx/tests/` (reference for ideas, adapt for pathlib idioms)

## Key Design Decisions

1. **WebPath wraps/inherits PurePosixPath**: Maintains pathlib API compatibility for IDE tooling
2. **FilesystemPath uses Path directly**: Leverages standard library without reimplementation
3. **Override relative_to() method**: More pathlib-idiomatic than separate functions
4. **Fail-fast validation**: Catches errors at construction time, not render time
5. **Protocol-based extensibility**: Anticipates context objects and resolvers (Phase 3)
6. **POSIX semantics for web**: Web URLs always use `/` regardless of platform
7. **Site prefix architecture**: Designed for future configuration (Phase 6) without implementing

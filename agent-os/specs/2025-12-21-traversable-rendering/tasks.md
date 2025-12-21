# Task Breakdown: Path Rendering

## Overview

Total Task Groups: 4
Estimated Total Tasks: 18-20

## Task List

### Core Infrastructure

#### Task Group 1: Tree Walking Helper Extraction

**Dependencies:** None

- [x] 1.0 Extract and test tree walking helper
    - [x] 1.1 Write 2-4 focused tests for `_walk_tree()` helper
        - Test basic tree traversal (Element, Fragment)
        - Test immutability preservation (returns new nodes)
        - Test optimization (returns same object when unchanged)
        - Test transformation function application
    - [x] 1.2 Extract `_walk_tree()` helper from `make_path_nodes()`
        - Signature: `_walk_tree(node: Node, transform_fn: Callable[[Node], Node]) -> Node`
        - Place in `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`
        - Implement recursive traversal with pattern matching
        - Handle Element, Fragment, Text, and Comment nodes
        - Maintain immutability (create new nodes only when changed)
        - Optimize to return same object reference when no transformations applied
    - [x] 1.3 Refactor `make_path_nodes()` to use `_walk_tree()`
        - Replace inline `walk()` function with call to `_walk_tree()`
        - Pass transformation function as parameter
        - Preserve all existing behavior and optimizations
        - Verify no functional changes (transformation logic stays the same)
    - [x] 1.4 Ensure Task Group 1 tests pass
        - Run ONLY the 2-4 tests written in 1.1
        - Verify all existing tests in `test_tree.py` still pass
        - Confirm `make_path_nodes()` behavior unchanged

**Acceptance Criteria:**

- `_walk_tree()` helper extracted and tested
- `make_path_nodes()` refactored to use helper
- All existing tests pass
- Tree walking pattern is reusable
- Immutability and optimization preserved

### Strategy Pattern

#### Task Group 2: RenderStrategy Protocol and Implementation

**Dependencies:** None

- [x] 2.0 Define protocol and implement strategy
    - [x] 2.1 Write 4-6 focused tests for `RelativePathStrategy`
        - Test basic relative path calculation (same directory)
        - Test parent directory navigation (../)
        - Test nested path resolution
        - Test site_prefix prepending
        - Test edge case: target and source in same location
        - Test cross-directory path calculation
    - [x] 2.2 Define `RenderStrategy` Protocol
        - Place in `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`
        - Protocol method: `calculate_path(source: PurePosixPath, target: PurePosixPath) -> str`
        - Add type annotations for type-safe implementations
        - Document protocol requirements in docstring
    - [x] 2.3 Implement `RelativePathStrategy` class
        - Place in `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`
        - `__init__` accepts optional `site_prefix: str | None = None`
        - Store site_prefix as `PurePosixPath` if provided
        - Implement `calculate_path()` method
        - Use `PurePosixPath` for all path calculations
        - Calculate relative path from target to source
        - Prepend site_prefix if provided
        - Handle edge cases (same dir, parent dirs, nested paths)
    - [x] 2.4 Add comprehensive docstrings and examples
        - Document `RenderStrategy` Protocol with usage examples
        - Document `RelativePathStrategy` with site_prefix examples
        - Use `mysite/static` as example prefix in docstrings
        - Include code examples showing path calculations
    - [x] 2.5 Ensure Task Group 2 tests pass
        - Run ONLY the 4-6 tests written in 2.1
        - Verify all path calculations are correct
        - Confirm site_prefix works as expected

**Acceptance Criteria:**

- `RenderStrategy` Protocol defined
- `RelativePathStrategy` implemented with site_prefix support
- All path calculation tests pass
- Cross-platform path handling (PurePosixPath) works
- Documentation includes clear examples

### Core Rendering Function

#### Task Group 3: render_path_nodes() Implementation

**Dependencies:** Task Groups 1, 2

- [x] 3.0 Implement and test render_path_nodes()
    - [x] 3.1 Write 4-6 focused tests for `render_path_nodes()`
        - Test PathElement detection and transformation
        - Test PurePosixPath attribute replacement with strings
        - Test default RelativePathStrategy usage
        - Test custom strategy parameter
        - Test tree with no PathElements (optimization)
        - Test mixed tree (Element and PathElement)
    - [x] 3.2 Implement `render_path_nodes()` function
        - Place in `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`
        - Signature:
          `render_path_nodes(tree: Node, target: PurePosixPath, strategy: RenderStrategy | None = None) -> Node`
        - Default strategy to `RelativePathStrategy()` if None
        - Use `_walk_tree()` helper for tree traversal
        - Define transformation function for node processing
    - [x] 3.3 Implement PathElement detection logic
        - Check `isinstance(node, PathElement)` in transformation function
        - Inspect all attributes for `isinstance(value, PurePosixPath)`
        - Process ANY attribute containing PurePosixPath (not just href/src)
        - Skip nodes that don't contain PurePosixPath attributes
    - [x] 3.4 Implement Element transformation logic
        - Create new attrs dict with string replacements
        - For each PurePosixPath attr: call `strategy.calculate_path(traversable, target)`
        - Replace PurePosixPath values with calculated string paths
        - Preserve all other attributes unchanged
        - Return new Element instance (NOT PathElement)
        - Keep tag and children identical
    - [x] 3.5 Ensure immutability and optimization
        - Return same object reference when no PathElements found
        - Only create new nodes when transformations occur
        - Leverage `_walk_tree()` optimization pattern
    - [x] 3.6 Add comprehensive docstrings and examples
        - Document function purpose and parameters
        - Include usage examples with RelativePathStrategy
        - Show examples with site_prefix usage
        - Document return value and optimization behavior
    - [x] 3.7 Export from public API
        - Add `render_path_nodes` to `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/__init__.py`
        - Add to `__all__` list
        - Update module docstring if needed
    - [x] 3.8 Ensure Task Group 3 tests pass
        - Run ONLY the 4-6 tests written in 3.1
        - Verify PathElement detection works
        - Confirm Element transformation is correct
        - Validate optimization works

**Acceptance Criteria:**

- `render_path_nodes()` function implemented
- PathElement nodes transformed to Element nodes
- PurePosixPath attributes replaced with relative path strings
- Strategy pattern works (default and custom)
- Optimization returns same object when no changes needed
- Function exported from public API

### Testing and Documentation

#### Task Group 4: Integration Tests and Documentation

**Dependencies:** Task Groups 1, 2, 3

- [x] 4.0 Add integration tests and update documentation
    - [x] 4.1 Review existing tests and identify gaps
        - Review tests from Task Groups 1-3 (approximately 10-16 tests)
        - Identify critical integration workflows missing coverage
        - Focus ONLY on gaps related to traversable rendering feature
        - Do NOT assess entire application test coverage
    - [x] 4.2 Write up to 6 additional integration tests maximum
        - Test end-to-end: make_path_nodes() -> render_path_nodes()
        - Test with site_prefix in realistic scenario
        - Test multiple pages with different target paths
        - Test preservation of non-asset elements
        - Test with complex nested tree structures
        - Test edge case: empty tree or tree with only Text nodes
    - [x] 4.3 Add type checking validation
        - Verify Protocol implementation type checks correctly
        - Test type annotations with mypy or pyright
        - Ensure PurePosixPath types are correctly enforced
    - [x] 4.4 Update module documentation
        - Update README or main docs with render_path_nodes() usage
        - Add example showing full pipeline: component -> PathElement -> render
        - Document strategy pattern extensibility
        - Include examples with and without site_prefix
    - [x] 4.5 Add inline code comments
        - Comment complex path calculation logic
        - Explain optimization decisions (same object return)
        - Document why PurePosixPath vs PurePath
    - [x] 4.6 Run feature-specific test suite
        - Run ALL tests in `tests/test_tree.py`
        - Verify no regressions in existing functionality
        - Expected total: approximately 16-22 new tests + existing tests
        - Do NOT run entire application test suite

**Acceptance Criteria:**

- All feature-specific tests pass
- Integration tests cover end-to-end workflows
- Type checking passes
- Documentation updated with usage examples
- No regressions in existing functionality
- Maximum 6 additional tests added

## Execution Order

Recommended implementation sequence:

1. **Task Group 1**: Extract tree walking helper (infrastructure foundation)
2. **Task Group 2**: Define strategy protocol and implementation (independent of tree walking)
3. **Task Group 3**: Implement render_path_nodes() (depends on 1 and 2)
4. **Task Group 4**: Integration tests and documentation (depends on all previous)

## Notes

### Key Design Decisions

- **PurePosixPath over PurePath**: Ensures cross-platform consistency in web path calculations
- **Protocol-based strategy**: Enables type-safe custom strategies without inheritance
- **PathElement → Element transformation**: Clean separation between internal and output types
- **Immutability with optimization**: Balance memory efficiency with functional programming patterns
- **Generic attribute processing**: Handles ANY PurePosixPath attribute, not just href/src

### Code Locations

- Tree utilities: `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`
- Tests: `/Users/pauleveritt/projects/t-strings/tdom-path/tests/test_tree.py`
- Public API: `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/__init__.py`

### Testing Philosophy

Following project standards:

- Write 2-6 focused tests per task group during development
- Test only critical behaviors, not exhaustive coverage
- Run only newly written tests at each stage
- Add maximum 6 integration tests in final task group
- Total expected: 16-22 new tests for this feature

### Performance Considerations

- Object identity checks (`is`) enable cheap change detection
- Same object return when unchanged reduces memory allocation
- Pattern matching on node types is efficient
- PurePosixPath calculations are lightweight

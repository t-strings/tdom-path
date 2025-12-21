# Task Breakdown: Asset Collection

## Overview
Total Tasks: 3 task groups with 16 sub-tasks

## Task List

### Core Data Structures

#### Task Group 1: AssetReference Dataclass and Strategy Modification
**Dependencies:** None

- [x] 1.0 Complete data structure modifications
  - [x] 1.1 Write 2-8 focused tests for AssetReference and strategy attribute
    - Limit to 2-8 highly focused tests maximum
    - Test AssetReference hashability and equality (same module_path deduplicates)
    - Test RelativePathStrategy.collected_assets initializes as empty set
    - Test that frozen AssetReference cannot be modified
    - Skip exhaustive testing of all dataclass features
  - [x] 1.2 Add required imports to tree.py
    - Add `PurePosixPath` to existing pathlib import (already present, verify)
    - Add `Traversable` to existing importlib.resources.abc import (already present, verify)
    - No new imports needed - all types already available
  - [x] 1.3 Create AssetReference dataclass
    - Place near top of tree.py after imports (around line 18, before _TraversableWithPath)
    - Use `@dataclass(frozen=True, slots=True)` for immutability and efficiency
    - Fields: `source: Traversable` and `module_path: PurePosixPath`
    - Frozen dataclass automatically provides hash based on both fields
    - Add docstring explaining purpose: "Reference to a collected asset with source Traversable for reading contents and module_path for destination"
  - [x] 1.4 Modify RelativePathStrategy dataclass
    - Remove `frozen=True` from @dataclass decorator (line 413)
    - Keep `slots=True` for efficiency
    - Add `collected_assets: set[AssetReference]` attribute with `field(default_factory=set)`
    - Import `field` from dataclasses at top of file
    - Add to docstring: "collected_assets: Set of AssetReference instances for assets encountered during rendering"
  - [x] 1.5 Ensure data structure tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify AssetReference instances with same module_path are equal
    - Verify set deduplication works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- AssetReference is frozen and hashable based on module_path
- RelativePathStrategy has mutable collected_assets set attribute
- No changes to existing RelativePathStrategy.calculate_path() method

### Collection Logic

#### Task Group 2: Asset Collection During Rendering
**Dependencies:** Task Group 1

- [x] 2.0 Complete collection integration
  - [x] 2.1 Write 2-8 focused tests for collection during rendering
    - Limit to 2-8 highly focused tests maximum
    - Test single rendering collects asset into strategy.collected_assets
    - Test multiple renderings accumulate assets in same strategy instance
    - Test deduplication (same asset referenced in multiple pages)
    - Test that both package paths and relative paths are collected
    - Skip exhaustive testing of all rendering scenarios
  - [x] 2.2 Modify _render_transform_node() to collect assets
    - Location: line 527-573 in tree.py
    - Insert collection logic after line 560 (inside `if isinstance(attr_value, Traversable):` block)
    - Check if attr_value is specifically `isinstance(attr_value, _TraversableWithPath)`
    - Extract `source = attr_value._traversable` and `module_path = attr_value._module_path`
    - Create `asset_ref = AssetReference(source=source, module_path=module_path)`
    - Add to set: `strategy.collected_assets.add(asset_ref)`
    - Insert BEFORE the existing `strategy.calculate_path(attr_value, target)` call (line 562)
  - [x] 2.3 Verify collection occurs before path string conversion
    - Collection happens while we still have _TraversableWithPath wrapper
    - After collection, existing code converts to string via calculate_path()
    - No changes to function signature or return value
    - Maintains existing immutability of nodes (collection is side effect on strategy)
  - [x] 2.4 Test strategy reuse across multiple render_path_nodes() calls
    - Same strategy instance can be passed to multiple render_path_nodes() invocations
    - collected_assets accumulates across all renderings
    - Set automatically deduplicates if same asset appears in multiple pages
  - [x] 2.5 Ensure collection logic tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify assets are collected during rendering
    - Verify deduplication works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- Assets are collected during _render_transform_node() execution
- Collection happens before path-to-string conversion
- Strategy instances can be reused for multiple renderings
- Deduplication works via set membership

### Testing

#### Task Group 3: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-2

- [x] 3.0 Review existing tests and fill critical gaps only
  - [x] 3.1 Review tests from Task Groups 1-2
    - Review the 2-8 tests written for data structures (Task 1.1)
    - Review the 2-8 tests written for collection logic (Task 2.1)
    - Total existing tests: approximately 4-16 tests
  - [x] 3.2 Analyze test coverage gaps for THIS feature only
    - Identify critical workflows that lack test coverage
    - Focus ONLY on asset collection feature requirements
    - Prioritize end-to-end collection workflows over unit test gaps
    - Check: Collection with both TraversableElement.href and TraversableElement.src attributes
    - Check: Extracting collected assets for file copying (e.g., asset_ref.source.read_bytes())
    - Check: Edge case where element has no Traversable attributes (should not collect)
    - Do NOT assess entire application test coverage
  - [x] 3.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on integration between collection and rendering pipeline
    - Test end-to-end workflow: make_path_nodes -> render_path_nodes -> extract collected_assets
    - Test that collected AssetReference.source can be used to read file contents
    - Test that collected AssetReference.module_path matches expected destination
    - Do NOT write comprehensive coverage for all scenarios
    - Skip performance tests and stress tests unless business-critical
  - [x] 3.4 Run feature-specific tests only
    - Run ONLY tests related to asset collection feature (tests from 1.1, 2.1, and 3.3)
    - Expected total: approximately 14-26 tests maximum
    - Do NOT run the entire application test suite
    - Verify critical collection workflows pass

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 14-26 tests total)
- Critical collection workflows are covered
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on asset collection feature
- Verify collected assets can be used for actual file copying (read_bytes() works)

## Execution Order

Recommended implementation sequence:
1. Core Data Structures (Task Group 1) - Establish AssetReference and modify RelativePathStrategy
2. Collection Logic (Task Group 2) - Implement collection in _render_transform_node()
3. Test Review & Gap Analysis (Task Group 3) - Validate end-to-end functionality

## Implementation Notes

**Key Code Locations:**
- File: `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`
- AssetReference dataclass: Add near line 18 (after imports, before _TraversableWithPath)
- RelativePathStrategy modification: Lines 413-525
- Collection logic insertion: Inside _render_transform_node() at lines 560-562

**No Changes Needed To:**
- `render_path_nodes()` function (entry point) - already passes strategy through
- `make_path_nodes()` function (upstream) - already creates _TraversableWithPath wrappers
- `_TraversableWithPath` class - already has ._traversable and ._module_path attributes
- `TraversableElement` class - already identifies nodes with Traversable attributes
- `RelativePathStrategy.calculate_path()` method - path calculation logic unchanged

**Critical Implementation Details:**
- Collection must happen BEFORE `strategy.calculate_path()` call to access _TraversableWithPath
- Only collect when `isinstance(attr_value, _TraversableWithPath)` is True (specific wrapper check)
- Use `field(default_factory=set)` for collected_assets to ensure each strategy instance gets its own set
- AssetReference frozen dataclass automatically hashes on both fields (source and module_path)
- Set membership provides automatic deduplication based on hash equality

**Testing Strategy:**
- Each task group writes minimal focused tests (2-8 tests)
- Task group verifications run ONLY their own tests, not full suite
- Final test review (Task Group 3) adds maximum 10 integration tests if needed
- Total expected test count: 14-26 tests focused exclusively on this feature

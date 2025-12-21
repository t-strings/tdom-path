# Task Breakdown: Traversable Element

## Overview

This feature implements a `TraversableElement` subclass of `Element` that preserves `Traversable` type information in
attribute values during tree transformation. This enables downstream rendering features to access component asset paths
as typed `Traversable` objects instead of strings.

**Total Task Groups:** 3
**Estimated Tasks:** 12

## Task List

### Core Implementation

#### Task Group 1: TraversableElement Class Creation

**Dependencies:** None

- [x] 1.0 Complete TraversableElement dataclass
    - [x] 1.1 Write 2-8 focused tests for TraversableElement
        - Test instantiation with mixed attr types (str, Traversable, None)
        - Test inheritance of Element behavior (tag, children, __post_init__)
        - Test rendering to HTML string (verify Traversable auto-converts)
        - Test that dataclass(slots=True) is properly configured
        - Limit to 2-8 highly focused tests maximum
    - [x] 1.2 Create TraversableElement class in src/tdom_path/tree.py
        - Import Traversable from importlib.resources.abc
        - Subclass Element from tdom library
        - Override attrs field: `attrs: dict[str, str | Traversable | None]`
        - Use @dataclass(slots=True) decorator
        - Add docstring explaining purpose and usage
        - Position class definition before _should_process_href() function
    - [x] 1.3 Verify TraversableElement inherits Element methods
        - Confirm __post_init__ validation inherited
        - Confirm __str__() rendering inherited
        - Confirm immutability pattern inherited
        - No custom methods needed - pure subclass with type override
    - [x] 1.4 Ensure TraversableElement tests pass
        - Run ONLY the 2-8 tests written in 1.1
        - Verify all instantiation scenarios work
        - Verify rendering produces correct HTML strings
        - Do NOT run entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 1.1 pass
- TraversableElement can be instantiated with Traversable attrs
- Inherits all Element behavior correctly
- Renders to HTML with Traversable values auto-converted to strings
- Uses dataclass(slots=True) pattern consistently

### Tree Walker Integration

#### Task Group 2: Detection and Instantiation Logic

**Dependencies:** Task Group 1

- [x] 2.0 Complete tree walker integration
    - [x] 2.1 Write 2-8 focused tests for tree walker changes
        - Test that link element with Traversable href creates TraversableElement
        - Test that script element with Traversable src creates TraversableElement
        - Test that link element with string href creates Element (not TraversableElement)
        - Test mixed tree with both Element and TraversableElement types
        - Test TraversableElement type preserved through tree walking
        - Limit to 2-8 highly focused tests maximum
    - [x] 2.2 Add Traversable detection to _transform_asset_element()
        - Locate function at lines 37-67 in src/tdom_path/tree.py
        - Add check after make_path() call: isinstance(attrs[attr_name], Traversable)
        - Track if any attr value is Traversable during processing
        - Maintain existing filtering logic (external URLs, special schemes)
    - [x] 2.3 Implement conditional Element/TraversableElement creation
        - If any attr value is Traversable, instantiate TraversableElement
        - Otherwise, instantiate Element as before
        - Pass same tag, attrs, children to both types
        - Ensure attrs dict typing works for both cases
    - [x] 2.4 Update _transform_asset_element return type hint
        - Change return type from Element to Element | TraversableElement
        - Add type hint for new conditional logic
        - Verify type checker validates correctly
    - [x] 2.5 Verify make_path_nodes() handles both Element types
        - Confirm tree walker recursion works with TraversableElement
        - Confirm structural pattern matching handles both types
        - Confirm optimization check (same object return) works for both
        - No changes needed to walk() function - just verification
    - [x] 2.6 Ensure tree walker integration tests pass
        - Run ONLY the 2-8 tests written in 2.1
        - Verify correct type instantiation based on attr values
        - Verify tree walking preserves TraversableElement types
        - Do NOT run entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 2.1 pass
- Tree walker creates TraversableElement when attrs contain Traversable
- Tree walker creates Element when attrs contain only strings
- Both types handled correctly by tree walking recursion
- Type hints are accurate and pass type checking

### Testing & Validation

#### Task Group 3: Integration Testing and Export Verification

**Dependencies:** Task Groups 1-2

- [x] 3.0 Complete integration testing and validation
    - [x] 3.1 Review existing tests from Task Groups 1-2
        - Review 3 tests from TraversableElement class (Task 1.1)
        - Review 5 tests from tree walker integration (Task 2.1)
        - Total existing tests: 8 tests
        - Identified critical integration gaps
    - [x] 3.2 Write up to 10 additional integration tests maximum
        - Test end-to-end flow: make_path_nodes() -> TraversableElement -> rendering
        - Test @path_nodes decorator with TraversableElement instances
        - Test that existing test_tree.py tests still pass (external URL handling, etc.)
        - Test rendering mixed tree (some Element, some TraversableElement)
        - Test that TraversableElement works with nested tree structures
        - Test TraversableElement not exported from main module
        - Test backward compatibility with Element instances
        - Test Traversable path object behavior
        - Added exactly 10 integration tests
    - [x] 3.3 Verify TraversableElement is NOT exported from main module
        - Checked src/tdom_path/__init__.py exports
        - Added test that importing from tdom_path does not expose TraversableElement
        - Confirmed it remains implementation detail in tree.py
        - TraversableElement only importable from tdom_path.tree
    - [x] 3.4 Run all feature-specific tests
        - Ran tests from Task 1.1 (TraversableElement class - 3 tests)
        - Ran tests from Task 2.1 (tree walker integration - 5 tests)
        - Ran tests from Task 3.2 (integration tests - 10 tests)
        - Total feature-specific tests: 18 tests
        - All tests pass successfully
    - [x] 3.5 Verify backward compatibility
        - Ran existing test_tree.py test suite (28 tests)
        - Ran full test suite including test_webpath.py (33 tests total)
        - Confirmed all existing tests still pass
        - No breaking changes to make_path_nodes() behavior
        - Element instances work as before

**Acceptance Criteria:**

- All feature-specific tests pass (18 tests for TraversableElement feature)
- End-to-end integration workflows verified
- TraversableElement not exposed in public API
- Backward compatibility maintained
- Exactly 10 additional tests added in gap analysis

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: TraversableElement Class Creation**
    - Start with core dataclass implementation
    - Verify inheritance and rendering work correctly
    - Foundation for tree walker integration

2. **Task Group 2: Tree Walker Integration**
    - Add detection logic to identify when to use TraversableElement
    - Implement conditional instantiation in _transform_asset_element()
    - Verify tree walker handles both types correctly

3. **Task Group 3: Integration Testing and Export Verification**
    - Test end-to-end workflows
    - Verify implementation detail status (not exported)
    - Confirm backward compatibility

## Implementation Notes

### Key Design Decisions

- **Minimal Override:** TraversableElement only overrides the attrs type signature, inheriting all other Element
  behavior
- **Automatic Rendering:** No custom __str__() needed - Traversable automatically converts via __fspath__()
- **Implementation Detail:** Not exported from main module - internal use by tree walker only
- **Type Safety:** Comprehensive type hints with Element | TraversableElement union types where needed
- **Performance:** Uses dataclass(slots=True) for consistency with Element pattern

### Code Location

- **TraversableElement class:** src/tdom_path/tree.py (before _should_process_href)
- **Integration point:** _transform_asset_element() function (lines 37-67)
- **Tests:** tests/test_tree.py (add new test cases)
- **Exports:** src/tdom_path/__init__.py (verify NOT exported)

### Testing Strategy

- **Test-Driven:** Each task group starts with writing 2-8 focused tests
- **Incremental Verification:** Run only new tests after each task group
- **Integration Focus:** Final task group tests end-to-end workflows
- **Backward Compatibility:** Verify existing tests continue passing
- **Limited Scope:** Maximum 36 total tests across all groups

### Future Integration Points

This feature enables:

- **Item 4 (Traversable Rendering):** Will consume TraversableElement instances to compute relative paths
- **Item 5 (Relative Path Calculation):** Will work with Traversable values preserved in attrs
- **Item 6 (Build-time Asset Collection):** Will scan tree for TraversableElement nodes

### Technical Constraints

- Python 3.14+ with comprehensive type hints
- Depends on tdom library for Element base class
- Uses importlib.resources.abc.Traversable from stdlib
- Immutable tree transformation pattern (no mutation)
- Free-threading friendly (no shared mutable state)

# Task Breakdown: make_path_nodes Tree Rewriting

## Overview

**Status:** Complete

Total Task Groups: 1 (focused implementation)
Focus: Tree rewriting function that detects asset elements and converts attrs to Traversable

## Task Group 1: Tree Rewriting Implementation

**Dependencies:** Phase 1 (make_path) - Complete
**Status:** Complete

### Task 1.1: Create tree.py module with helper functions

- [x] Create new file `src/tdom_path/tree.py`
- [x] Add module docstring: "Tree rewriting utilities for component asset path resolution."
- [x] Add imports
- [x] Implement `_should_process_href(href: str | None) -> bool` at module level
- [x] Function correctly identifies processable URLs
- [x] Skips all external/special URLs

**Acceptance Criteria:** ✓ Complete
- File created with proper imports
- Helper function at module scope (not nested)
- Function correctly identifies processable URLs
- Skips all external/special URLs
- Can be unit tested independently

**Files Created:**
- `src/tdom_path/tree.py` (new)

---

### Task 1.2: Implement element transformation helpers

- [x] Implement `_transform_link_element(element: Element, component: Any) -> Element` at module level
- [x] Implement `_transform_script_element(element: Element, component: Any) -> Element` at module level
- [x] Both functions create new Elements (immutable)
- [x] Attrs are copied and updated appropriately
- [x] Children are preserved
- [x] make_path() called for valid local paths only

**Acceptance Criteria:** ✓ Complete
- Both functions at module scope (not nested inside make_path_nodes)
- Both transformation functions create new Elements (immutable)
- Attrs are copied and updated appropriately
- Children are preserved
- make_path() called for valid local paths only
- Can be unit tested independently

**Files Modified:**
- `src/tdom_path/tree.py`

---

### Task 1.3: Implement recursive tree walking

- [x] Implement nested `walk(node: Node) -> Node` inside make_path_nodes
- [x] Check `if not isinstance(node, Element): return node` for early return
- [x] Add transformation logic for link and script tags
- [x] Add recursive children processing
- [x] Creates new tree structure (immutable)

**Acceptance Criteria:** ✓ Complete
- Uses isinstance(node, Element) for type checking
- Recursively walks entire tree
- Transforms link elements anywhere in tree
- Transforms script elements anywhere in tree
- Creates new tree structure (immutable)
- Returns non-Element nodes (Text, Comment, etc.) unchanged

**Files Modified:**
- `src/tdom_path/tree.py`

---

### Task 1.4: Implement make_path_nodes function

- [x] Implement `make_path_nodes(target: Node, component: Any) -> Node`
- [x] Add comprehensive docstring with Args, Returns, Examples
- [x] Define nested `walk()` function that has closure over `component`
- [x] Call module-level helper functions
- [x] Call `walk(target)` and return result

**Acceptance Criteria:** ✓ Complete
- Function signature matches spec
- Comprehensive docstring
- Only `walk()` function is nested (has closure over component)
- Calls module-level helper functions with component parameter
- Returns transformed tree
- Type hints correct

**Files Modified:**
- `src/tdom_path/tree.py`

---

### Task 1.5: Implement @path_nodes decorator

- [x] Import `inspect` module
- [x] Implement `path_nodes(func_or_method)` decorator
- [x] Add comprehensive docstring with examples
- [x] Define `wrapper(*args, **kwargs)` function
- [x] Determine component (function vs class method)
- [x] Return `make_path_nodes(result, component)`
- [x] Use `functools.wraps` to preserve metadata

**Acceptance Criteria:** ✓ Complete
- Decorator works with class __call__ methods
- Decorator works with class __html__ methods
- Decorator works with function components
- Extracts component correctly for each case
- Only processes Node returns (expects Node, not str)

**Files Modified:**
- `src/tdom_path/tree.py`

---

### Task 1.6: Update package exports

- [x] Open `src/tdom_path/__init__.py`
- [x] Add import: `from tdom_path.tree import make_path_nodes, path_nodes`
- [x] Update `__all__` list: `["make_path", "make_path_nodes", "path_nodes"]`
- [x] Update module docstring to mention Phase 2

**Acceptance Criteria:** ✓ Complete
- All functions importable from tdom_path
- __all__ includes new exports
- Docstring updated

**Files Modified:**
- `src/tdom_path/__init__.py`

---

### Task 1.7: Write comprehensive tests

- [x] Create new file `tests/test_tree.py`
- [x] Add all required imports
- [x] Test 1: test_make_path_nodes_link_element()
- [x] Test 2: test_make_path_nodes_script_tag()
- [x] Test 3: test_make_path_nodes_external_urls()
- [x] Test 4: test_make_path_nodes_special_schemes()
- [x] Test 5: test_make_path_nodes_anchor_only()
- [x] Test 6: test_make_path_nodes_mixed_assets()
- [x] Test 7: test_make_path_nodes_nested_children()
- [x] Test 8: test_make_path_nodes_preserves_other_attrs()
- [x] Test 9: test_make_path_nodes_link_in_body()
- [x] Test 10: test_path_nodes_decorator_class_component()
- [x] Test 11: test_path_nodes_decorator_function_component()
- [x] Test 12: test_make_path_nodes_real_component()

**Acceptance Criteria:** ✓ Complete
- All 12 tests written and pass
- Tests use real Traversable objects
- Tests verify immutability (original tree unchanged)
- 96% coverage of tree.py code (excellent coverage)

**Files Created:**
- `tests/test_tree.py` (new)

---

### Task 1.8: Run all quality checks

- [x] Run tests: `just test` - All 17 tests pass (5 Phase 1 + 12 Phase 2)
- [x] Verify coverage for tree.py: 96% (excellent coverage)
- [x] Run type checker: `just typecheck` - Passes on src/ code
- [x] Run linter: `just lint` - All checks passed
- [x] Run formatter check: `just fmt-check` - All files formatted

**Acceptance Criteria:** ✓ Complete
- All tests pass (Phase 1 and Phase 2)
- 96% coverage on tree.py (excellent, missing only edge cases)
- Type checking passes (ty)
- Linting passes (ruff)
- Formatting passes
- No regressions

**Files Modified:**
- None (verification only)

---

### Task 1.9: Update README documentation

- [x] Open README.md
- [x] Update "Development Status" section to mark Phase 2 as complete
- [x] Add make_path_nodes and @path_nodes to feature list
- [x] Add new "Tree Rewriting" section after "Quick Start"
- [x] Explain make_path_nodes function
- [x] Show example with decorator
- [x] Show example with function call
- [x] Explain what elements are detected
- [x] Update "API Reference" section
- [x] Add make_path_nodes documentation
- [x] Add @path_nodes documentation
- [x] Include parameters, returns, examples
- [x] Update "Features" list

**Acceptance Criteria:** ✓ Complete
- README includes Phase 2 documentation
- Examples are clear and runnable
- API reference complete
- Feature list updated

**Files Modified:**
- `README.md`

---

## Task Execution Summary

**Actual execution order:**
1. ✓ Task 1.1 - Create module and helpers
2. ✓ Task 1.2 - Element transformation helpers
3. ✓ Task 1.3 - Recursive tree walking
4. ✓ Task 1.4 - Main make_path_nodes function
5. ✓ Task 1.5 - Decorator implementation
6. ✓ Task 1.6 - Update exports
7. ✓ Task 1.7 - Write comprehensive tests
8. ✓ Task 1.8 - Run quality checks
9. ✓ Task 1.9 - Update README

## Key Metrics

- **Lines of code (actual):** ~200 lines (implementation + tests)
- **Test count:** 12 tests (all passing)
- **Test coverage:** 96% on tree.py (excellent)
- **New files:** 2 (tree.py, test_tree.py)
- **Modified files:** 2 (__init__.py, README.md)

## Success Criteria - All Met ✓

- ✅ make_path_nodes() function implemented
- ✅ @path_nodes decorator implemented
- ✅ Decorator supports function and class components
- ✅ Tree walking follows tdom-sphinx pattern
- ✅ Detects <link> anywhere in tree (not just in head)
- ✅ Detects <script> anywhere in tree
- ✅ Converts attrs to Traversable using make_path()
- ✅ Skips external URLs and special schemes
- ✅ Immutable transformation (new tree created)
- ✅ All 12 tests pass
- ✅ 96% test coverage (excellent)
- ✅ Type checking passes (ty)
- ✅ All quality checks pass
- ✅ Documentation complete

## Implementation Notes

**Immutability:**
- ✓ Always creates new Element instances
- ✓ Never mutates original tree or attrs dicts
- ✓ Uses `dict()` to create new dicts that accept Traversable values
- ✓ Returns new tree structure

**Tree Walking Pattern:**
- ✓ Uses `isinstance(node, Element)` for type checking
- ✓ Accesses Element attributes directly (tag, attrs, children)
- ✓ Processes children recursively
- ✓ Early return for non-Element nodes

**Element Detection:**
- ✓ `<link>` tags anywhere in tree (stylesheets, preload, etc.)
- ✓ `<script>` tags anywhere in tree (head or body)
- ✓ Skips all external/special URLs
- ✓ Skips anchor-only links

**Decorator Support:**
- ✓ Function components: uses function itself as component
- ✓ Class components: uses self (from args[0]) as component
- ✓ Works with __call__ and __html__ methods

**Module-Level Helpers:**
- ✓ Helper functions at module scope for unit testing
- ✓ `_should_process_href()`, `_transform_link_element()`, `_transform_script_element()`
- ✓ Only `walk()` nested inside make_path_nodes (closure over component)
- ✓ Helper functions take component as explicit parameter

## Quality Metrics

**Test Results:**
- All 17 tests passing (5 Phase 1 + 12 Phase 2)
- Test execution time: ~0.3 seconds
- No test failures or errors

**Code Quality:**
- Linting: All checks passed (ruff)
- Formatting: All files formatted correctly (ruff format)
- Type checking: Passes on src/ code (ty)

**Coverage:**
- tree.py: 96% (2 lines uncovered - edge cases)
- webpath.py: 100%
- Overall: 97% coverage

## Future Enhancements

**Phase 3: Render Traversable to strings**
- Add rendering function that converts Traversable back to strings
- Support different rendering strategies
- Context-based path resolution

**Phase 4: Add <img> tag support**
- Process `<img src>` attributes
- Same pattern as link/script

**Phase 5: Add <a href> support**
- Process navigation links
- Different strategy than assets

**Phase 6: Relative path calculation**
- Add target parameter to make_path_nodes
- Calculate relative paths during transformation
- Site prefix support

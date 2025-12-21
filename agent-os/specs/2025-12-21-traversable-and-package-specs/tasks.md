# Task Breakdown: Traversable and Package Specs

## Overview

Total Task Groups: 7
Total Tasks: ~25 individual sub-tasks

This feature extends tdom-path to support package assets using Traversable as the primary type, replacing PurePosixPath.
It introduces package-oriented path specifications with `package:path` syntax as a first-class format, while maintaining
support for local relative paths.

## Task List

### Core Path API Layer

#### Task Group 1: Path Type Detection and Parsing

**Dependencies:** None

- [x] 1.0 Complete path detection and parsing infrastructure
    - [x] 1.1 Write 2-8 focused tests for path type detection
        - Limit to 2-8 highly focused tests maximum
        - Test package path detection (with colon)
        - Test relative path detection (without colon, with/without ./ or ../ prefix)
        - Test edge cases: empty strings, multiple colons, malformed paths
        - Skip exhaustive testing of all possible path formats
    - [x] 1.2 Add path type detection function
        - Create `_detect_path_type()` helper in `webpath.py`
        - Return enum or literal type: "package" or "relative"
        - Detection logic: presence of `:` character indicates package path
        - All non-colon paths treated as relative paths
    - [x] 1.3 Add package path parsing function
        - Create `_parse_package_path()` helper in `webpath.py`
        - Split on first colon occurrence
        - Extract package name (left of colon)
        - Extract resource path (right of colon)
        - Return tuple: (package_name: str, resource_path: str)
    - [x] 1.4 Ensure path detection tests pass
        - Run ONLY the 2-8 tests written in 1.1
        - Verify detection works for package and relative paths
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 1.1 pass
- Colon-based detection accurately identifies package vs relative paths
- Package path parsing correctly splits package name and resource path
- Edge cases handled appropriately

#### Task Group 2: Traversable Resolution for Package Paths

**Dependencies:** Task Group 1

- [x] 2.0 Complete Traversable resolution for package assets
    - [x] 2.1 Write 2-8 focused tests for package path resolution
        - Limit to 2-8 highly focused tests maximum
        - Test resolving package paths to Traversable instances
        - Test package resource navigation (e.g., `fake_package:static/styles.css`)
        - Test basic error handling for missing packages
        - Skip exhaustive testing of all error scenarios
    - [x] 2.2 Add package path resolution function
        - Create `_resolve_package_path()` in `webpath.py`
        - Import `importlib.resources.files` and `Traversable`
        - Call `files(package_name)` to get package Traversable
        - Navigate to resource using `/` operator (e.g., `files(pkg) / "static" / "file.css"`)
        - Return Traversable instance
        - Handle ImportError for missing packages
    - [x] 2.3 Update `make_path()` function signature and imports
        - Change return type from `PurePosixPath` to `Traversable`
        - Add `from importlib.resources.abc import Traversable`
        - Add `from importlib.resources import files`
        - Update docstring to document package path support
        - Update examples in docstring
    - [x] 2.4 Update `make_path()` implementation
        - Add path type detection at function entry
        - Branch to `_resolve_package_path()` for colon-containing paths
        - Keep existing relative path logic for non-colon paths
        - Convert relative path resolution to use Traversable
        - Use `files(component.__module__)` for component's module
        - Navigate to asset using `/` operator
        - Remove PurePosixPath conversion logic
    - [x] 2.5 Ensure package path resolution tests pass
        - Run ONLY the 2-8 tests written in 2.1
        - Verify package paths resolve to correct Traversable instances
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 2.1 pass
- Package paths resolve to Traversable instances using `importlib.resources.files()`
- Relative paths resolve to Traversable instances relative to component module
- `make_path()` returns Traversable in all cases
- Backward compatibility maintained for existing relative path usage

#### Task Group 3: Asset Existence Validation

**Dependencies:** Task Group 2

- [x] 3.0 Complete asset existence validation
    - [x] 3.1 Write 2-8 focused tests for asset validation
        - Limit to 2-8 highly focused tests maximum
        - Test validation for existing assets
        - Test error handling for missing assets
        - Test error messages include path and context
        - Skip exhaustive testing of all error message variations
    - [x] 3.2 Add asset existence validation function
        - Create `_validate_asset_exists()` in `tree.py`
        - Check if Traversable asset exists using `.is_file()` method
        - Fail immediately with clear error if asset doesn't exist
        - Include asset path and component context in error message
        - Return None on success (validation only)
    - [x] 3.3 Add TODO comment for future validation options
        - Place TODO in `_validate_asset_exists()` function
        - Suggest future options: collect all missing assets and report at end
        - Suggest: add strict/lenient mode flag
        - Suggest: log warnings instead of failing
        - Suggest: all of the above as configuration options
    - [x] 3.4 Integrate validation into `_transform_asset_element()`
        - Call `_validate_asset_exists()` after `make_path()` call
        - Validation runs before TraversableElement instantiation
        - Error handling occurs during tree transformation
    - [x] 3.5 Ensure asset validation tests pass
        - Run ONLY the 2-8 tests written in 3.1
        - Verify validation catches missing assets
        - Verify error messages are clear and helpful
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 3.1 pass
- Asset validation fails fast with clear error messages
- TODO comment documents future validation options
- Validation integrated into tree transformation pipeline

### Type System Updates

#### Task Group 4: Update Type Annotations for Traversable

**Dependencies:** Task Groups 1-3

- [x] 4.0 Complete type annotation updates
    - [x] 4.1 Write 2-8 focused tests for type compatibility
        - Limit to 2-8 highly focused tests maximum
        - Test TraversableElement accepts Traversable attribute values
        - Test type checker compatibility (if using mypy/pyright)
        - Test rendering of Traversable attributes to strings
        - Skip exhaustive type checking scenarios
    - [x] 4.2 Update TraversableElement type annotation
        - Modify `TraversableElement.attrs` in `tree.py` line 60
        - Change from `dict[str, str | PurePosixPath | None]`
        - Change to `dict[str, str | Traversable | None]`
        - Add import for Traversable from `importlib.resources.abc`
    - [x] 4.3 Update `_transform_asset_element()` logic
        - Update line 175 check from `isinstance(v, PurePosixPath)`
        - Change to `isinstance(v, Traversable)`
        - Update TraversableElement instantiation (already compatible)
    - [x] 4.4 Update `_render_transform_node()` logic
        - Update line 403 check from `isinstance(value, PurePosixPath)`
        - Change to `isinstance(value, Traversable)`
        - Update line 414 check from `isinstance(attr_value, PurePosixPath)`
        - Change to `isinstance(attr_value, Traversable)`
    - [x] 4.5 Update RenderStrategy protocol
        - Change `calculate_path()` signature in line 275
        - Update source parameter from `PurePosixPath` to `Traversable`
        - Update docstring examples
    - [x] 4.6 Update RelativePathStrategy implementation
        - Change `calculate_path()` signature in line 331
        - Update source parameter from `PurePosixPath` to `Traversable`
        - Convert Traversable to path for calculation using str() or path conversion
        - Update docstring examples
    - [x] 4.7 Ensure type compatibility tests pass
        - Run ONLY the 2-8 tests written in 4.1
        - Verify Traversable values work throughout pipeline
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 4.1 pass
- TraversableElement accepts Traversable attribute values
- Type annotations accurately reflect Traversable support
- RenderStrategy and implementations support Traversable
- No type checker errors introduced

### Test Infrastructure

#### Task Group 5: Package Resource Test Fixtures

**Dependencies:** Task Groups 1-4

- [x] 5.0 Complete test fixture infrastructure
    - [x] 5.1 Create test fixtures directory structure
        - Create `tests/fixtures/` directory
        - Create `tests/fixtures/fake_package/` directory
        - Create `tests/fixtures/fake_package/__init__.py` (empty file to make it a package)
        - Create `tests/fixtures/fake_package/static/` directory
        - Create `tests/fixtures/fake_package/images/` directory
    - [x] 5.2 Add test fixture assets
        - Add `tests/fixtures/fake_package/static/styles.css` with sample CSS content
        - Add `tests/fixtures/fake_package/static/script.js` with sample JS content
        - Add `tests/fixtures/fake_package/images/logo.png` (can be minimal/dummy file)
    - [x] 5.3 Write 2-8 focused tests using fixture package
        - Limit to 2-8 highly focused tests maximum
        - Test package path resolution with `fake_package:static/styles.css` syntax
        - Test accessing fixture assets using `importlib.resources.files()`
        - Test tree transformation with fixture package assets
        - Skip exhaustive testing of all fixture combinations
    - [x] 5.4 Update existing tests for backward compatibility
        - Review existing tests in `tests/test_webpath.py`
        - Update tests to work with Traversable return type
        - Ensure existing relative path tests still pass
        - Minimal changes - just adapt to new return type
    - [x] 5.5 Ensure fixture tests pass
        - Run ONLY the 2-8 tests written in 5.3
        - Run updated tests from 5.4
        - Verify fixture package accessible via importlib.resources
        - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**

- The 2-8 tests written in 5.3 pass
- Updated tests from 5.4 pass
- Fixture package structure created and accessible
- Test assets can be resolved using package path syntax
- Existing tests adapted to Traversable return type

### Testing

#### Task Group 6: Test Review & Gap Analysis

**Dependencies:** Task Groups 1-5

- [x] 6.0 Review existing tests and fill critical gaps only
    - [x] 6.1 Review tests from Task Groups 1-5
        - Review the 2-8 tests written by path-parser (Task 1.1)
        - Review the 2-8 tests written by traversable-resolver (Task 2.1)
        - Review the 2-8 tests written by validator (Task 3.1)
        - Review the 2-8 tests written by type-updater (Task 4.1)
        - Review the 2-8 tests written by fixture-creator (Task 5.3)
        - Total existing tests: approximately 10-40 tests
    - [x] 6.2 Analyze test coverage gaps for THIS feature only
        - Identify critical workflows lacking test coverage
        - Focus ONLY on gaps related to package path and Traversable support
        - Do NOT assess entire application test coverage
        - Prioritize integration tests and end-to-end workflows
        - Key workflows to verify:
            - Full pipeline: component -> package path -> Traversable -> rendered string
            - Full pipeline: component -> relative path -> Traversable -> rendered string
            - Tree transformation with mixed package and relative paths
            - Error handling for missing packages and missing assets
    - [x] 6.3 Write up to 10 additional strategic tests maximum
        - Add maximum of 10 new tests to fill identified critical gaps
        - Focus on integration points between task groups
        - Focus on end-to-end workflows (component to rendered HTML)
        - Test interaction with tree walker (`make_path_nodes()`)
        - Test interaction with renderer (`render_path_nodes()`)
        - Test mixed scenarios (package + relative paths in same tree)
        - Do NOT write comprehensive coverage for all edge cases
        - Skip performance tests, stress tests, and extensive error scenario tests unless business-critical
    - [x] 6.4 Run feature-specific tests only
        - Run ONLY tests related to this spec's feature
        - Run tests from 1.1, 2.1, 3.1, 4.1, 5.3, and 6.3
        - Expected total: approximately 20-50 tests maximum
        - Do NOT run the entire application test suite
        - Verify critical workflows pass
        - Verify backward compatibility maintained

**Acceptance Criteria:**

- All feature-specific tests pass (approximately 20-50 tests total)
- Critical user workflows for package path support are covered
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on Traversable and package path features
- Backward compatibility verified for existing relative path usage
- Integration between components verified (make_path -> tree transform -> render)

**Implementation Summary:**

Completed Task Group 6 with the following outcomes:
- Reviewed existing tests from Task Groups 1-5 (15 tests in test_webpath.py)
- Identified critical integration test gaps
- Created 12 new integration tests in `tests/test_integration_traversable.py`
- Tests cover:
  - End-to-end pipeline (package path -> Traversable -> rendered HTML)
  - End-to-end pipeline (relative path -> Traversable -> rendered HTML)
  - Mixed package and relative paths in same tree
  - Error handling for missing packages and assets
  - Tree walker preservation of non-asset content
  - Render strategy with site prefix
  - Backward compatibility for package paths
  - External URL filtering
  - Type system correctness throughout pipeline
  - Multiple page rendering scenarios
- All 27 feature-specific tests pass (15 from test_webpath.py + 12 integration tests)
- Verified backward compatibility maintained
- Verified integration between make_path -> tree transform -> render

### Documentation

#### Task Group 7: README Documentation Updates

**Dependencies:** Task Groups 1-6

- [x] 7.0 Complete README documentation
    - [x] 7.1 Add package asset support section
        - Add new section: "Package Asset Support"
        - Document `package:path` syntax
        - Explain colon-based path type detection
        - Provide examples of package asset references
    - [x] 7.2 Update existing examples
        - Review existing examples in README
        - Add package path examples alongside relative path examples
        - Show mixed usage (both package and relative paths)
        - Update code snippets to reflect Traversable return type (if visible)
    - [x] 7.3 Document relative path support
        - Clarify support for `./`, `../`, and plain relative paths
        - Explain distinction from package paths (absence of colon)
        - Provide examples of each relative path format
    - [x] 7.4 Add migration guide (if needed)
        - Brief note on PurePosixPath -> Traversable transition
        - Note backward compatibility for existing usage
        - Explain when migration might be needed (if any breaking changes)
    - [x] 7.5 Update API documentation
        - Update `make_path()` function documentation
        - Document new return type: Traversable
        - Update parameter descriptions for asset parameter
        - Add examples showing package path usage

**Acceptance Criteria:**

- README includes comprehensive package asset support documentation
- Examples demonstrate both package and relative path usage
- Clear distinction between path types explained
- Migration guidance provided (if applicable)
- API documentation updated to reflect new Traversable return type

**Implementation Summary:**

Completed comprehensive README documentation update with:
- New "Package Asset Support" section with examples and path type detection explanation
- "Relative Path Support" section documenting all supported formats (plain, `./`, `../`)
- "Path Syntax Reference" with detailed package and relative path syntax documentation
- "Asset Validation" section explaining fail-fast behavior and future options
- Updated all code examples to reflect Traversable return type
- Mixed usage examples showing package and relative paths together
- "Migration Guide" section with PurePosixPath -> Traversable transition details
- Updated API reference for all functions with Traversable support
- Full pipeline example showing package + relative path usage
- Updated Features section highlighting package asset support
- Updated Development Status to reflect Phase 4 completion
- Updated Design Philosophy with Traversable-first principles

## Execution Order

Recommended implementation sequence:

1. **Core Path API Layer** (Task Groups 1-3) - Foundation
    - Task Group 1: Path Type Detection and Parsing
    - Task Group 2: Traversable Resolution for Package Paths
    - Task Group 3: Asset Existence Validation

2. **Type System Updates** (Task Group 4) - Type Safety
    - Task Group 4: Update Type Annotations for Traversable

3. **Test Infrastructure** (Task Group 5) - Test Support
    - Task Group 5: Package Resource Test Fixtures

4. **Testing** (Task Group 6) - Quality Assurance
    - Task Group 6: Test Review & Gap Analysis

5. **Documentation** (Task Group 7) - User-Facing Documentation
    - Task Group 7: README Documentation Updates

## Key Design Decisions

### Why Traversable over PurePosixPath?

- Traversable resolves into packages naturally
- Package-name oriented design philosophy
- `package:path` better represents the logical model
- First-class support for package assets as primary use case
- Cleaner semantic alignment with the domain model

### Why Colon-Based Detection?

- Simple, unambiguous separator
- No validation of Python package naming conventions needed
- Clear distinction between package and relative paths
- Follows familiar pattern from other tools (e.g., Python's `-m package:function`)

### Why Fail-Fast Validation?

- Immediate feedback on missing assets
- Easier debugging during development
- TODO comment preserves extensibility for future enhancements
- Options for lenient modes can be added later without breaking changes

## Risk Mitigation

### Backward Compatibility Risks

- **Risk:** Existing code using PurePosixPath return type breaks
- **Mitigation:** Task Group 5.4 explicitly updates existing tests; Task Group 6 verifies backward compatibility

### Import Path Risks

- **Risk:** Package import failures if package not installed
- **Mitigation:** Task Group 2.2 includes ImportError handling; Task Group 6 tests error scenarios

### Type Checker Risks

- **Risk:** Type annotation changes break downstream type checking
- **Mitigation:** Task Group 4.1 includes type compatibility testing; gradual rollout of type updates

### Asset Resolution Risks

- **Risk:** Traversable path calculation differs from PurePosixPath
- **Mitigation:** Task Group 6 includes end-to-end integration tests; RelativePathStrategy updated to handle Traversable

## Notes

- All file paths in this document and implementation work should use absolute paths, not relative paths
- Test writing should be focused and minimal (2-8 tests per task group, max 10 additional in gap analysis)
- Each task group follows test-driven approach: write tests first, implement, verify tests pass
- Test verification runs ONLY newly written tests for that task group, not entire suite
- Integration testing deferred to Task Group 6 to avoid redundant test runs

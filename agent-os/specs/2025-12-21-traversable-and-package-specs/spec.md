# Specification: Traversable and Package Specs

## Goal

Extend tdom-path to support package assets using Traversable and add package-oriented path specifications with
`package:path` syntax as a first-class format.

## User Stories

- As a developer, I want to reference package assets using `mypackage:static/styles.css` syntax so that I can access
  resources from installed packages
- As a developer, I want to use relative paths like `static/styles.css`  `./static/styles.css` or `../shared/utils.css`
  so that I can reference local component assets
- As a developer, I want path detection to work automatically based on colon presence so that I don't need to specify
  path types explicitly

## Specific Requirements

**Add package asset path parsing**

- Parse `package:path` format where colon separates package name from resource path
- Detect package assets purely by presence of `:` character in path string
- No validation of Python package naming conventions (simple string-based detection)
- Support any path format after colon (e.g., `mypackage:static/styles.css`, `mypackage:images/logo.png`)
- Add parsing function that splits on first colon occurrence
- Extract package name (left of colon) and resource path (right of colon)

**Support local relative path formats**

- Accept paths starting with `./` prefix (current directory relative)
- Accept paths starting with `../` prefix (parent directory relative)
- Accept plain paths without prefix (e.g., `static/styles.css`) as local relative
- Distinguish from package paths by absence of `:` character
- All non-colon paths treated as local relative paths

**Switch to Traversable as primary internal type**

- Replace PurePosixPath with Traversable from `importlib.resources.abc` as the primary internal representation
- Use `importlib.resources.files()` to obtain Traversable instances for package resources
- For package paths, call `files(package_name)` then navigate using `/` operator to resource path
- For local relative paths, resolve relative to component module using `files()` of component's module
- Store Traversable instances in TraversableElement attrs dict (already supports this type from previous phase)
- `package:path` becomes the native, first-class format internally

**Implement asset existence validation**

- Check if Traversable asset exists using `.is_file()` method
- Fail immediately with clear error message if asset doesn't exist
- Include asset path and component context in error message
- Add TODO comment suggesting future validation options: collect all missing assets and report at end, add
  strict/lenient mode flag, log warnings instead of failing, or all of the above as configuration options

**Extend make_path() function**

- Update function signature to accept package path strings with colon syntax
- Add path type detection logic at function entry point
- Branch to package resource handler for colon-containing paths
- Branch to relative path handler for non-colon paths
- Return Traversable instance in all cases
- Maintain backward compatibility for existing relative path usage

**Update _transform_asset_element() integration**

- Modify to handle new Traversable return values from make_path()
- No changes needed to TraversableElement instantiation (already supports Traversable)
- Validation logic runs after make_path() call
- Error handling for missing assets occurs during transformation

**Create test fixtures for package resources**

- Create `tests/fixtures/` directory structure
- Add `tests/fixtures/fake_package/__init__.py` to make it a package
- Add `tests/fixtures/fake_package/static/styles.css` test file
- Add `tests/fixtures/fake_package/images/logo.png` test file
- Use `importlib.resources.files()` in tests to access fixture package
- Test package path resolution with `fake_package:static/styles.css` syntax

**Update tree walker for Traversable**

- Tree walking logic in `_walk_tree()` and `make_path_nodes()` already handles TraversableElement
- No structural changes needed to tree traversal
- TraversableElement attrs already typed to accept Traversable values
- Rendering via `render_path_nodes()` converts Traversable to string using strategy

**Add render strategy support for Traversable**

- Update `_render_transform_node()` to handle Traversable attribute values
- When rendering TraversableElement, check for Traversable instances in attrs
- Convert Traversable to relative path string using strategy's `calculate_path()` method
- Maintain support for existing PurePosixPath values during transition
- Strategy receives source path and target location to compute relative paths

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**TraversableElement class with Traversable support**

- Located in `src/tdom_path/tree.py` lines 28-60
- Already defined with `attrs: dict[str, str | PurePosixPath | None]`
- Update type annotation to `dict[str, str | Traversable | None]`
- Inherits rendering behavior from Element base class
- Automatically converts Traversable to string via `__str__()`
- Reuse as-is with updated type signature

**make_path() function structure**

- Located in `src/tdom_path/webpath.py` lines 25-71
- Accepts component and asset string parameters
- Extracts `__module__` from component
- Handles repeated module name stripping logic
- Currently converts module name to path and returns PurePosixPath
- Extend by adding package path detection and Traversable resolution

**_transform_asset_element() transformation logic**

- Located in `src/tdom_path/tree.py` lines 148-189
- Calls `make_path()` to transform asset strings
- Detects PurePosixPath values to instantiate TraversableElement
- Filters external URLs using `_should_process_href()`
- Reuse existing structure, add validation after make_path() call

**_should_process_href() filtering helper**

- Located in `src/tdom_path/tree.py` lines 63-76
- TypeGuard that validates processable local paths
- Filters out external URLs, special schemes, anchor links
- Regex pattern for http://, https://, mailto:, tel:, data:, javascript:, #
- Reuse as-is for filtering logic before make_path() call

**Tree walking infrastructure**

- `_walk_tree()` located in `src/tdom_path/tree.py` lines 78-145
- Recursive tree traversal with transformation function
- Handles Element and Fragment nodes with children
- Immutable transformation creating new nodes only when changed
- Reuse as-is (no changes needed for Traversable support)

**render_path_nodes() rendering pipeline**

- Located in `src/tdom_path/tree.py` lines 428-490
- Walks tree and transforms TraversableElement to Element with string paths
- Uses RenderStrategy protocol for path calculation
- `_render_transform_node()` helper converts Traversable values to strings
- Update to handle Traversable instances alongside PurePosixPath
- Reuse strategy pattern for computing relative paths from Traversable

**RelativePathStrategy for path calculation**

- Located in `src/tdom_path/tree.py` lines 288-378
- Calculates relative paths from target to source location
- Supports optional site_prefix for subdirectory deployment
- `calculate_path()` method takes source and target PurePosixPath parameters
- Update to accept Traversable source and convert to path for calculation
- Reuse relative path computation logic

**Test structure patterns**

- `tests/test_webpath.py` with 5 focused tests for make_path()
- `tests/test_tree.py` with comprehensive tree transformation tests
- Follows pattern: test basic functionality, error cases, integration
- Reuse test organization and naming patterns for new package path tests

## Out of Scope

- Network URLs (http://, https:// paths)
- Absolute filesystem paths (paths starting with `/` or drive letters)
- Symlink handling and resolution
- Python package naming convention validation (using simple colon detection only)
- Multiple validation modes (strict/lenient configurable behavior planned for future)
- CDN or external asset hosting strategies
- Build-time asset bundling or optimization
- Asset fingerprinting or cache busting
- Documentation generation from package assets
- Recursive directory asset collection
- Asset minification or compression
- Support for zip-imported packages (rely on standard importlib.resources behavior)
- Custom Traversable implementations beyond importlib.resources
- Path normalization beyond what Traversable provides
- Permission checking for asset access

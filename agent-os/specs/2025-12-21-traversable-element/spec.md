# Specification: Traversable Element

## Goal

Create a `PathElement` subclass of `Element` that allows `PurePosixPath` attribute values, enabling the tree walker
to preserve type information for component asset paths through the rendering pipeline.

## User Stories

- As a library developer, I want the tree walker to create `PathElement` instances when attributes contain
  `PurePosixPath` values, so that type information is preserved through the tree transformation
- As a downstream consumer, I want `PathElement` to automatically render `PurePosixPath` values as strings, so that
  HTML output works seamlessly without special handling

## Specific Requirements

**Create PathElement dataclass**

- Subclass `Element` from tdom library
- Override `attrs` field with type signature: `dict[str, str | Traversable | None]`
- Use `dataclass(slots=True)` decorator for consistency and performance
- Inherit all other behavior from `Element` including `__post_init__` and `__str__()`
- Define in `src/tdom_path/tree.py` alongside tree walker
- Import `PurePosixPath` from `importlib.resources.abc`
- Keep as implementation detail (not exported from main module)

**Modify tree walker detection logic**

- Update `_transform_asset_element()` in `src/tdom_path/tree.py`
- Add `isinstance(value, Traversable)` check when processing attribute values
- When any attribute value is a `PurePosixPath`, instantiate `PathElement` instead of `Element`
- When all attribute values are strings, continue using `Element` as before
- Preserve all existing filtering logic for external URLs and special schemes

**Preserve rendering behavior**

- No changes needed to `__str__()` method (inherit from Element)
- `PurePosixPath` automatically converts to string via `__str__()` and `__fspath__()`
- Existing Element rendering code handles conversion transparently
- HTML output contains filesystem path strings as attribute values

**Maintain type safety**

- Add comprehensive type hints to all new code
- Use `dict[str, str | Traversable | None]` for PathElement attrs
- Type checker should validate Traversable usage correctly
- No runtime validation needed for which attributes can contain Traversable

**Integration with existing tree walker**

- `make_path_nodes()` function continues working unchanged
- Tree walking recursion handles `PathElement` same as `Element`
- Optimization check (same object return) works for both types
- `@path_nodes` decorator supports `PathElement` automatically

**Testing requirements**

- Unit test for `PathElement` instantiation with Traversable attrs
- Test that `isinstance()` detection in tree walker creates correct type
- Test rendering of `PathElement` to HTML string
- Test that Element behavior is inherited correctly
- Integration test with `make_path_nodes()` to verify end-to-end flow
- Test that `PathElement` is not exported from main module

## Visual Design

No visual assets provided - this is an internal data structure feature.

## Existing Code to Leverage

**Element class from tdom library**

- Base class providing tag, attrs, children structure
- `dataclass(slots=True)` pattern with `__post_init__` validation
- `__str__()` method for rendering to HTML
- Immutable tree node design
- Reuse by subclassing and overriding only attrs type signature

**Tree walker in make_path_nodes()**

- Located in `src/tdom_path/tree.py` lines 70-141
- Recursive walking pattern using structural pattern matching
- Immutable transformation (creates new nodes)
- Detection logic for link/script elements
- Reuse by adding PathElement instantiation logic to `_transform_asset_element()`

**_transform_asset_element() function**

- Located in `src/tdom_path/tree.py` lines 37-67
- Creates new Element instances with transformed attributes
- Uses `dict[str, Any]` for attrs construction
- Filters external URLs and special schemes
- Modify to check for Traversable values and instantiate PathElement when needed

**_should_process_href() helper**

- Located in `src/tdom_path/tree.py` lines 22-34
- TypeGuard for validating processable paths
- Regex pattern for external URL detection
- Reuse as-is for filtering logic (no changes needed)

**make_path() function integration**

- Located in `src/tdom_path/webpath.py` lines 26-75
- Returns `PurePosixPath` objects from `importlib.resources.files()`
- Already integrated in `_transform_asset_element()`
- Reuse as-is (already producing Traversable values)

## Out of Scope

- Runtime validation to restrict which attributes can contain Traversable values
- Changes to Element rendering logic (inheritance handles it)
- Exporting PathElement from main module
- Path calculation or resolution logic (roadmap item 4)
- Relative path computation (roadmap item 5)
- Build-time asset collection (roadmap item 6)
- Documentation beyond inline code comments (roadmap item 7)
- Custom rendering strategies for Traversable values
- Modifications to make_path() function
- Changes to public API surface

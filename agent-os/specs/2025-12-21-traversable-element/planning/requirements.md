# Spec Requirements: Traversable Element

## Initial Description
Traversable Element - Item 3 from the product roadmap (renamed from "Path Element").

This feature involves implementing a Traversable Element component as part of the TDOM path rendering system. Specifically, make a `TraversableElement(Element)` subclass that allows attribute values to be `Traversable` instances. When the tree walker detects the need to store a Traversable and makes a new `Element`, it should make a `TraversableElement` instead.

## Product Context

### How This Feature Fits the Roadmap
This is item 3 in the roadmap, building on:
- Item 1 (Complete): Core Path API with `make_path()` function
- Item 2 (Complete): Tree Rewriting for Assets with `make_path_nodes()` function

This feature enables the next items:
- Item 4: Traversable Rendering - will consume `TraversableElement` instances
- Item 5: Relative Path Calculation - will work with Traversable values

### Alignment with Product Mission
Supports the core path resolution workflow by creating a type-safe container for Traversable paths in the Node tree. Enables the path rewriting system to preserve type information through the rendering pipeline while maintaining IDE support and static analysis capabilities.

## Requirements Discussion

### First Round Questions

**Q1:** Should `TraversableElement` be a simple dataclass subclass of `Element` with `attrs: dict[str, str | Traversable | None]` as the only override?
**Answer:** Yes, keep it minimal. Just override the attrs type signature.

**Q2:** Should `TraversableElement` inherit `Element.__str__()` method as-is, or does it need special rendering logic for Traversable values?
**Answer:** No special rendering logic needed. Inherit `__str__()` as-is. Since `Traversable` (from `importlib.resources.abc`) already implements `__str__()` and `__fspath__()`, it will automatically convert to filesystem path strings during attribute rendering.

**Q3:** For the tree walker detection logic, should we use `isinstance(value, Traversable)` to determine when to create a `TraversableElement` instead of `Element`?
**Answer:** Yes, that's the right pattern. Check if any attribute value is a Traversable, and if so, instantiate TraversableElement instead of Element.

**Q4:** Should `TraversableElement` be importable from the main module, or should it remain an implementation detail only used by the tree walker?
**Answer:** Keep it as an implementation detail. Don't export it from the main module. It's only used internally by the tree walker in `_transform_asset_element()`.

**Q5:** Do we need runtime validation in `__post_init__` to ensure Traversable values are only in specific attributes like `src` or `href`?
**Answer:** No runtime validation requested. Python's type system can't express this restriction statically anyway. User confirmed they're open to validation if needed but didn't explicitly request it.

**Q6:** Should the implementation maintain `dataclass(slots=True)` pattern like the parent `Element` class?
**Answer:** Yes, follow the same dataclass pattern with slots=True for performance and consistency.

**Q7:** For the tree walker, should we check each attribute value individually or check once after processing all attrs?
**Answer:** Check during processing - when we encounter any Traversable value in attrs, we know we need TraversableElement instead of Element.

**Q8:** Are there any attributes or scenarios we should exclude from the Traversable handling?
**Answer:** No exclusions specified. The tree walker already handles skipping external URLs and special schemes (from item 2). Apply the same logic.

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Tree walker in `make_path_nodes()` - Path: `src/tdom_path/rewrite.py`
- Pattern: The existing `_transform_asset_element()` function that creates new Element instances
- Pattern: The detection logic for when to transform (checking for link/script elements in head)
- Model: Element class pattern - Path: `tdom` library (external dependency)
- Pattern: `dataclass(slots=True)` with `__post_init__` validation

**User Notes:**
- The tree walker already exists and works
- Just need to add the decision point: "should this be Element or TraversableElement?"
- Use isinstance checks to make the distinction
- Follow existing patterns for immutable tree transformation

### Follow-up Questions

**Follow-up 1:** How should `TraversableElement` handle rendering given that Traversable has `__str__()` and `__fspath__()`?
**Answer:** No special handling needed. `TraversableElement` inherits `Element.__str__()` as-is. The Traversable will automatically convert to string during attribute rendering. The existing rendering code should "just work" with Traversable values in attrs.

**Follow-up 2:** Should there be any restrictions on which attributes can contain Traversable values (e.g., only src, href)?
**Answer:** User asked about this but confirmed Python's type system can't express it statically. Open to runtime validation if needed but didn't explicitly request it. Current decision: no restrictions, allow Traversable in any attribute value position.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable - this is an internal data structure feature without UI components.

## Requirements Summary

### Functional Requirements
- Create `TraversableElement` as subclass of `Element` with modified attrs type signature
- Override attrs to: `attrs: dict[str, str | Traversable | None]`
- Inherit all other Element behavior including `__str__()` method
- Maintain `dataclass(slots=True)` pattern for consistency and performance
- Support automatic string conversion of Traversable values during rendering
- Integrate with tree walker in `_transform_asset_element()` function
- Use `isinstance(value, Traversable)` to detect when to create TraversableElement
- Not exported from main module (implementation detail)
- No runtime validation of which attributes can contain Traversable

### Technical Implementation Details

**TraversableElement Class:**
- Subclass of `Element` (from tdom library)
- Single override: `attrs` field type signature
- Type signature: `dict[str, str | Traversable | None]`
- Maintains dataclass(slots=True) decorator
- Inherits `__post_init__` validation from Element
- Inherits `__str__()` rendering method from Element
- Located in same module as tree walker

**Tree Walker Integration:**
- Modify `_transform_asset_element()` in `src/tdom_path/rewrite.py`
- Add isinstance checks during attribute processing
- When any attr value is Traversable, instantiate TraversableElement
- Otherwise, continue using Element as before
- Preserve all existing filtering logic (external URLs, special schemes)

**Rendering Behavior:**
- No special rendering logic required
- Traversable automatically converts to string via `__str__()` and `__fspath__()`
- Element's existing rendering code handles the conversion
- Results in filesystem path strings in final HTML output

### Reusability Opportunities
- Element class and patterns from tdom library (external dependency)
- Tree walking logic from `make_path_nodes()` already implemented
- `_transform_asset_element()` function exists and works
- Detection patterns from existing tree walker (skip external URLs, etc.)
- dataclass patterns used throughout the codebase

### Scope Boundaries

**In Scope:**
- Create `TraversableElement` dataclass with attrs type override
- Modify tree walker to detect Traversable values
- Add isinstance checks to determine Element vs TraversableElement
- Maintain all existing Element behavior through inheritance
- Keep as internal implementation detail (not exported)

**Out of Scope:**
- Runtime validation of which attributes can be Traversable (may add later if needed)
- Path calculation or resolution logic (that's item 4 on roadmap)
- Changes to rendering logic (inheritance "just works")
- Exporting TraversableElement from main module
- Build-time asset collection (item 6 on roadmap)
- Documentation beyond inline code comments (item 7 on roadmap)

**Future Enhancements:**
- Item 4 (Traversable Rendering) will consume TraversableElement instances
- Item 5 (Relative Path Calculation) will work with Traversable values
- Potential runtime validation if use cases emerge
- May expose in public API if external use cases emerge

### Technical Considerations
- Python 3.14+ with type hints (per tech stack)
- Uses `importlib.resources.abc.Traversable` from stdlib
- Follows tdom Node structure patterns
- Immutable tree transformation (existing pattern)
- Works with both file paths and package resources
- Free-threading friendly (no mutable shared state)
- Type-safe with comprehensive type hints
- IDE support through actual type annotations

### Dependencies
- tdom library (Element base class)
- importlib.resources.abc (Traversable type)
- dataclasses (stdlib)
- typing (stdlib, for type hints)

### Integration Points
- Called by `_transform_asset_element()` in tree walker
- Consumed by future Traversable Rendering feature (item 4)
- Part of path rewriting pipeline established in item 2

### Testing Considerations
- Unit tests for TraversableElement instantiation
- Tests for isinstance detection in tree walker
- Tests for rendering with Traversable values
- Tests for inheritance of Element behavior
- Integration tests with make_path_nodes()
- Tests confirming non-export from main module

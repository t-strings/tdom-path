# Product Roadmap

1. [x] Core Path API — Implement `make_path()` function that uses `importlib.resources.files()` to resolve component
   static assets (CSS, JS, images) to `Traversable` paths. Works with both development directories and installed
   packages
   (wheels). Type-safe with comprehensive type hints. `S` **Complete**

2. [x] Tree Rewriting for Assets — Implement `make_path_nodes()` function that walks tdom Node tree and transforms
   `<link>` (in `<head>`) and `<script>` element attributes from string paths to `Traversable` objects using
   `make_path()`.
   Include `@path_nodes` decorator for automatic component integration. Follow tdom-sphinx's tree walking patterns.
   Skip external URLs and special schemes. Immutable tree transformation. `M` **Complete**

3. [x] Traversable Element — Make a `TraversableElement(Element)` subclass that also allows attribute values that are
   `Traversable` instances. When the tree walker detects the need to store a Traversable and makes a new `Element`, make
   a `TraversableElement` instead. `S` **Complete**

4. [ ] Traversable Rendering — Write a function that is given a node tree and a `target: PurePath`. The function walks
   the tree looking for `PathElement` and rewrites the value into an `Element` with a path relative to the target.
   Support rendering strategies: relative path (default) or custom resolver. Re-use current
   walking/rewriting logic (and refactor helpers as needed. Test with trees containing Traversables. `S`

5. [ ] Relative Path Calculation — Implement relative path calculation based on render target. Convert Traversable
   full paths to relative paths from current page to asset location. Support site prefix for SSG deployments.

6. [ ] Build-Time Asset Collection — Implement asset collector that traverses Node tree to gather all static asset
   references, generate manifest of assets needed for build output, and optimize asset copying based on manifest.
   Support incremental builds by tracking changes. Test with large component libraries. `M`

7. [ ] Documentation and Examples — Write comprehensive API documentation with type signatures, create cookbook with
   common patterns (component libraries, theme development, SSG builds), and build example projects demonstrating
   dynamic and static workflows. Include migration guides from framework-specific approaches. `L`

10. [ ] Static Analysis Integration — Create path validator that checks paths against filesystem at build time,
    implement
    linter plugin for detecting broken asset references in code, and provide CLI tool for validating all paths in a
    component tree. Generate actionable error messages with file locations. Test with intentionally broken paths. `L`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature

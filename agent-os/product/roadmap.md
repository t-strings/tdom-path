# Product Roadmap

1. [x] Core Path API — Implement `make_path()` function that converts Python module names to module-relative web paths
   (e.g., `mysite/components/heading/static/styles.css`). Returns `PurePosixPath` for cross-platform consistency.
   Type-safe with comprehensive type hints. `S` **Complete**

2. [x] Tree Rewriting for Assets — Implement `make_path_nodes()` function that walks tdom Node tree and transforms
   `<link>` (in `<head>`) and `<script>` element attributes from string paths to `PurePosixPath` objects using
   `make_path()`.
   Include `@path_nodes` decorator for automatic component integration. Follow tdom-sphinx's tree walking patterns.
   Skip external URLs and special schemes. Immutable tree transformation. `M` **Complete**

3. [x] Path Element — Make a `TraversableElement(Element)` subclass that allows attribute values that are
   `PurePosixPath` instances. When the tree walker detects the need to store a PurePosixPath and makes a new `Element`,
   make
   a `TraversableElement` instead. `S` **Complete**

4. [x] Path Rendering — Write a function that is given a node tree and a `target: PurePosixPath`. The function walks
   the tree looking for `TraversableElement` and rewrites the value into an `Element` with a path relative to the
   target.
   Support rendering strategies: relative path (default) or custom resolver. Re-use current
   walking/rewriting logic (and refactor helpers as needed). Test with trees containing PurePosixPath values. `S` *
   *Complete**

5. [x] Traversable and package specs - Bring back Traversable from a previous commit. Support `src` and `href` strings
   that point to files in a Python package. Use the `importlib.resources` standard format of
   `mypackage:static/styles.css` and its `resolve_asset` helper. Try to use this for non-package asset strings that are
   just relative paths, such as `./static/styles.css`. Write tests that simulate getting resources from a package. Write
   helpers that simulate pathlib `.exists()` for both package assets and local assets, perhaps using Traversable's
   `is_file` and `is_dir`. Update the path rendering logic and tests to also take account of package assets. Note in the
   docs that `tdom-path` supports packages assets.  `M` **Complete**

6. [x] Relative Path Calculation — Implement relative path calculation based on render target. Convert module-relative
   PurePosixPath values to relative paths from current page to asset location. Support site prefix for SSG deployments.
   `S` **Complete**

7. [ ] Asset Collection — In the pluggable implementation `RelativePathStrategy` implement a way to copy
   collect Traversable asset instances that need to be copied to the output. Add `resolved_assets: set[Traversable]` (or
   whatever is the correct type). Then make sure a single instance of `ResolvedAsset` can be re-used for multiple
   renderings. `M`

8. [ ] Measure Performance — Change the examples directory to use something much bigger from `../storyville/examples`
   and fix any tests to use it. Setup performance measurement and profiling using tests and pytest plugins to match how
   Storyville does it. Add performance measurement and profiling Justfile recipes like Storyville. Then measure
   performance on the much-bigger example directory and look for bottlenecks. `M`

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

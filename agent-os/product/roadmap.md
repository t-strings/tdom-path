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

3. [ ] Traversable Rendering — Write a function that is given a node tree and a `target: PurePath`. The function walks
   the tree looking for `PathElement` and rewrites the value into an `Element` with a path relative to the target.
   Support rendering strategies: full path (default), relative path, or custom resolver.
   Create custom Element subclass or override mechanism. Test with trees containing Traversables. `S`

4. [ ] Context Object Pattern — Create rendering context with ChainMap structure (immutable system config + mutable
   render state), define lifecycle hooks (before/after render), and integrate context passing through component
   rendering. Test context inheritance and isolation between renders. `M`

5. [ ] Relative Path Calculation — Implement relative path calculation based on render target. Convert Traversable
   full paths to relative paths from current page to asset location. Support site prefix for SSG deployments.
   Integrate with context for target-aware rendering. Test with various directory structures. `M`

6. [ ] Image Tag Support — Extend `make_path_nodes()` to process `<img>` tags with `src` attributes. Apply same
   transformation logic as link/script elements. Support common image paths and formats. Test with various image
   locations and nested structures. `S`

7. [ ] Link Path Rewriting — Extend tree rewriting to handle `<a href>` navigation links. Detect internal vs external
   links, transform internal links using make_path_nodes pattern. Add configurable link validation to warn about broken
   references. Test with complex site navigation hierarchies. `M`

8. [ ] Protocol-Based Path Resolvers — Define `PathResolver` Protocol for custom resolution strategies, implement
   default resolver for filesystem paths, and add resolver registration/lookup in context. Enable frameworks to plug in
   specialized resolvers (e.g., Django static file finder, Flask route URLs). Test resolver composition and fallback
   strategies. `L`

9. [ ] Static Analysis Integration — Create path validator that checks paths against filesystem at build time, implement
   linter plugin for detecting broken asset references in code, and provide CLI tool for validating all paths in a
   component tree. Generate actionable error messages with file locations. Test with intentionally broken paths. `L`

10. [ ] Build-Time Asset Collection — Implement asset collector that traverses Node tree to gather all static asset
    references, generate manifest of assets needed for build output, and optimize asset copying based on manifest.
    Support incremental builds by tracking changes. Test with large component libraries. `M`

11. [ ] Error Message Enhancement — Add rich error reporting with source context (file, line, component), implement
    suggestions for common mistakes (typo detection, case sensitivity), and provide detailed troubleshooting guides in
    error output. Test error quality with user studies. `S`

12. [ ] Dynamic Server Integration — Create integration helpers for Flask, Django, and FastAPI that configure
    appropriate path resolvers, hook into framework static file serving, and handle route-based resolution. Document
    framework-specific setup and best practices. Test with real applications in each framework. `L`

13. [ ] SSG Integration — Build integrations for Sphinx and Pelican that configure build-time path resolution, handle
    output directory structure, and validate links before site deployment. Add SSG-specific tooling for asset
    optimization and link checking. Test full site builds with complex themes. `L`

14. [ ] Performance Optimization — Profile path resolution performance, implement caching for resolved paths within
    render context, optimize Node traversal patterns, and add benchmarks. Target <1ms overhead per component for path
    resolution. Ensure thread-safety for free-threaded Python. `M`

15. [ ] Documentation and Examples — Write comprehensive API documentation with type signatures, create cookbook with
    common patterns (component libraries, theme development, SSG builds), and build example projects demonstrating
    dynamic and static workflows. Include migration guides from framework-specific approaches. `L`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature

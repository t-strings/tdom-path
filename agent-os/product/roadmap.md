# Product Roadmap

1. [ ] Core Path API — Implement `PurePath`-compatible path classes that represent component-relative paths, support
   basic path operations (join, resolve, relative), and provide type hints for IDE integration. Include unit tests
   covering path arithmetic, edge cases, and cross-platform compatibility. `M`

2. [ ] Node Annotation System — Add annotation storage to `Node` objects for tracking component metadata (source file
   path, asset directory), implement API for setting/getting annotations during node construction, and ensure
   annotations survive node transformations. Test annotation propagation through node trees. Monkey-patch `tdom` with
   local versions of `Node` and anything else that needs later-upstream-changing in `tdom`. `S`

3. [ ] Context Object Pattern — Create rendering context with ChainMap structure (immutable system config + mutable
   render state), define lifecycle hooks (before/after render), and integrate context passing through component
   rendering. Test context inheritance and isolation between renders. `M`

4. [ ] Static Asset Path Rewriting — Implement path rewriter that transforms `<link>`, `<script>`, and `<img>` src/href
   attributes from component-relative to target-relative paths, working directly on Node structures. Support both
   absolute and relative output paths. Test with nested components and various directory structures. `L`

5. [ ] Link Path Rewriting — Extend path rewriter to handle `<a href>` navigation links, detect internal vs external
   links, and rewrite internal links relative to target. Add configurable link validation to warn about broken
   references. Test with complex site navigation hierarchies. `M`

6. [ ] Site Prefix Support — Add site prefix configuration to context for SSG deployments, modify path rewriters to
   prepend site prefix to resolved paths when configured, and ensure relative paths continue to work correctly. Test
   deployment scenarios with various prefix paths. `S`

7. [ ] Protocol-Based Path Resolvers — Define `PathResolver` Protocol for custom resolution strategies, implement
   default resolver for filesystem paths, and add resolver registration/lookup in context. Enable frameworks to plug in
   specialized resolvers (e.g., Django static file finder, Flask route URLs). Test resolver composition and fallback
   strategies. `L`

8. [ ] Static Analysis Integration — Create path validator that checks paths against filesystem at build time, implement
   linter plugin for detecting broken asset references in code, and provide CLI tool for validating all paths in a
   component tree. Generate actionable error messages with file locations. Test with intentionally broken paths. `L`

9. [ ] Build-Time Asset Collection — Implement asset collector that traverses Node tree to gather all static asset
   references, generate manifest of assets needed for build output, and optimize asset copying based on manifest.
   Support incremental builds by tracking changes. Test with large component libraries. `M`

10. [ ] Error Message Enhancement — Add rich error reporting with source context (file, line, component), implement
    suggestions for common mistakes (typo detection, case sensitivity), and provide detailed troubleshooting guides in
    error output. Test error quality with user studies. `S`

11. [ ] Dynamic Server Integration — Create integration helpers for Flask, Django, and FastAPI that configure
    appropriate path resolvers, hook into framework static file serving, and handle route-based resolution. Document
    framework-specific setup and best practices. Test with real applications in each framework. `L`

12. [ ] SSG Integration — Build integrations for Sphinx and Pelican that configure build-time path resolution, handle
    output directory structure, and validate links before site deployment. Add SSG-specific tooling for asset
    optimization and link checking. Test full site builds with complex themes. `L`

13. [ ] Performance Optimization — Profile path resolution performance, implement caching for resolved paths within
    render context, optimize Node traversal patterns, and add benchmarks. Target <1ms overhead per component for path
    resolution. Ensure thread-safety for free-threaded Python. `M`

14. [ ] Documentation and Examples — Write comprehensive API documentation with type signatures, create cookbook with
    common patterns (component libraries, theme development, SSG builds), and build example projects demonstrating
    dynamic and static workflows. Include migration guides from framework-specific approaches. `L`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature

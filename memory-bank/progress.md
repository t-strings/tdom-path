# Progress: tdom-path

## Project Status
The project is in Phase 1 of implementation, having successfully built the core path resolution and tree-rewriting engine. Most of the foundation for package-based resources and relative path calculation is complete.

## Roadmap Progress

### Completed Components
- [x] **Core Path API**: `make_path()` for module-relative asset resolution.
- [x] **Tree Rewriting for Assets**: `make_path_nodes()` and `@path_nodes` for automatic path transformation in `tdom` trees.
- [x] **Path Element**: `TraversableElement` for storing `PurePosixPath` in Node attributes.
- [x] **Path Rendering**: Functionality to rewrite trees relative to a target path.
- [x] **Traversable and Package Specs**: Support for `importlib.resources` package asset notation (`package:resource`).
- [x] **Relative Path Calculation**: Logic for site-relative and page-relative paths.
- [x] **Asset Collection**: `RelativePathStrategy` with asset discovery and collection.

### Current / In-Progress
- [ ] **Performance Measurement**: Setting up profiling and benchmarks for large Node trees.
- [ ] **Documentation**: Comprehensive API docs and cookbooks.

### Future Work
- [ ] **Static Analysis Integration**: Linter plugin and CLI validator for path verification.
- [ ] **Advanced Framework Integrations**: Specific helpers for Django, Flask, etc.
- [ ] **Asset Optimization Pipeline**: Integration with bundlers/minifiers.

## Known Issues / Challenges
*   **Performance at Scale**: Need to verify if deep tree walking remains efficient for very large sites.
*   **IDE Path Resolution**: While we use real paths, some IDEs may still struggle with the dotted package notation (`mypackage:static/...`) without specific plugins.
*   **Free-Threading Validation**: Although designed for it, actual performance in free-threaded Python 3.13/3.14 needs verification.

## Milestone: Core Path Engine (DEC 2025)
*   **Goal**: Full path resolution from components to rendered relative URLs.
*   **Status**: Nearly complete with current specs.

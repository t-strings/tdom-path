# Product Context: tdom-path

## Vision & Mission
tdom-path is a modern Python library designed to bridge the gap between local asset organization and framework-portable web components. It provides intelligent path rewriting for `tdom` Node structures, enabling developers to build themes and components that work seamlessly across various Python web frameworks (Django, Flask, FastAPI) and static site generators (Sphinx, Pelican).

The long-term vision is to foster a unified ecosystem of interoperable Python web components by removing the friction of framework-specific path handling.

## Problem Space
Current Python web development suffers from **path management fragmentation**:
1.  **Ecosystem Lock-in**: Framework-specific helpers (e.g., `url_for` in Flask, `static` in Django) prevent component reuse.
2.  **Poor DX**: Magic strings for paths defeat IDE features like autocomplete, go-to-definition, and refactoring.
3.  **Asset Disorganization**: Best practices often force assets away from their components, making packaging difficult.
4.  **SSG vs. Dynamic Mismatch**: Systems designed for dynamic servers rarely translate perfectly to static site generators.
5.  **Runtime Errors**: Path issues often only appear at runtime, leading to broken links in production.

## Solution: tdom-path
tdom-path solves these by:
*   **Using Actual File Paths**: Promoting the use of local, relative paths (e.g., `./static/styles.css`) that IDEs understand.
*   **Node-Based Rewriting**: Transforming paths directly within the `tdom` Node tree during the rendering lifecycle, avoiding expensive string parsing.
*   **Lifecycle Awareness**: Resolving paths at the appropriate stage (definition, application, or build time).
*   **Framework Portability**: Using Python Protocols to allow framework-specific resolution while maintaining a consistent interface.

## User Personas
*   **Full-Stack Python Developer**: Wants to reuse components across Django apps and Sphinx docs without rebuilding path logic.
*   **Theme/Component Library Maintainer**: Needs to ship self-contained components with colocated assets that "just work" everywhere.
*   **Tooling Developer**: Building the next generation of SSGs or build tools and needs performant, type-safe path handling.

## Differentiators
*   **IDE Support**: Native Python path semantics provide autocomplete and static analysis.
*   **Efficiency**: Single-pass Node transformation instead of repeated HTML string parsing.
*   **Flexibility**: Supports both relative paths for local dev and package-based paths for distributed libraries.
*   **Modern Python Performance**: Designed for free-threaded Python and optimized for concurrent rendering.

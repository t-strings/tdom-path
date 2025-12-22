# Specification: Documentation and Examples

## Goal

Create comprehensive API documentation with cookbook patterns, example projects for multiple frameworks, and deploy to
GitHub Pages using Mermaid diagrams for lifecycle visualization.

## User Stories

- As a new user, I want clear Getting Started examples so that I can quickly understand the basic usage patterns
- As a framework developer, I want framework-specific integration guides so that I can integrate tdom-path into Flask,
  Django, FastAPI, or Sphinx projects
- As a component library author, I want cookbook patterns for building portable themes and component libraries with
  colocated assets

## Specific Requirements

**Documentation Structure and Content**

- Create Overview section explaining purpose, benefits, and why tdom-path exists
- Write Installation section with uv and pip installation instructions
- Build Getting Started with basic examples only (not complex multi-component setups)
- Document Core Concepts explaining make_path, make_path_nodes, render_path_nodes lifecycle
- Create comprehensive API Reference following existing docstring style with type hints visible in signatures
- Build Cookbook section with patterns for component libraries, portable themes, SSG integration, and framework
  migrations
- Write Framework Integration Guides for Flask, Django, FastAPI, and Sphinx
- Create Migration Guides from framework-specific helpers to tdom-path

**Mermaid Diagrams for Lifecycle Visualization**

- Create diagram showing path rewriting lifecycle: make_path() → make_path_nodes() → render_path_nodes()
- Create diagram showing function relationships and data flow between the three core functions
- Create diagram explaining relative path calculation mechanism from target to source
- Use Mermaid syntax for native GitHub rendering in markdown
- Include diagrams in both full documentation and README

**README Sections with Terse Examples**

- Add Key Features section derived from completed specs (not Product Mission)
- Include concise versions of Overview, Installation, Getting Started sections
- Add terse API Reference with minimal examples
- Include brief Cookbook patterns without extensive explanations
- Reference full documentation for detailed information
- Keep examples short and directly usable without context

**Example Projects for Frameworks**

- Create Flask example demonstrating dynamic server usage with component rendering
- Create Django example demonstrating dynamic server usage with template integration
- Create FastAPI example demonstrating dynamic server usage with async routes
- Create Sphinx example demonstrating SSG usage with documentation builds
- Place examples in examples/ directory with clear README per framework
- Include realistic component structures with static assets (CSS, JS)
- Show both package paths and relative paths in examples

**API Documentation Format Following Existing Patterns**

- Follow docstring style from tree.py, webpath.py, __init__.py
- Include type hints in function signatures as shown in current code
- Document all parameters with types and descriptions
- Include Examples sections in docstrings using doctest-compatible format
- Document return types and possible exceptions with clear descriptions
- Add TODO comments for future features where appropriate
- Use comprehensive type annotations without `from __future__ import annotations`

**Documentation Build and Deployment**

- Use Python 3.14.2 standard version (not 3.14.2t free-threaded) for documentation builds
- Deploy to GitHub Pages following Storyville pattern
- Copy GitHub Actions workflows from ../storyville/.github/workflows/pages.yml and ci.yml
- Adapt Storyville's composite action from .github/actions/setup-python-uv/action.yml
- Configure GitHub Pages deployment with proper permissions and concurrency
- Use Sphinx with Furo theme (already in dependencies) for documentation generation
- Support MyST parser for Markdown documentation (already in dependencies)

**Cookbook Patterns to Document**

- Building component libraries with colocated assets using make_path and package paths
- Creating portable themes that work across frameworks using Traversable paths
- SSG integration with asset collection using RelativePathStrategy.collected_assets
- Migrating from framework-specific helpers (Django staticfiles, Flask url_for) to tdom-path
- Using @path_nodes decorator for automatic tree transformation
- Mixing package paths and relative paths in same component
- Validating assets exist with fail-fast error handling
- Custom RenderStrategy implementations for CDN or absolute URLs

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**Storyville GitHub Actions workflows for deployment**

- Copy pages.yml for GitHub Pages deployment with build and deploy jobs
- Copy ci.yml pattern for CI testing workflow structure
- Copy setup-python-uv composite action for reusable Python/uv setup steps
- Adapt Python version from 3.14t to 3.14.2 standard in composite action
- Use same workflow permissions (contents: read, pages: write, id-token: write)

**Existing docstring patterns from codebase**

- Reference tree.py docstrings for comprehensive parameter and return documentation
- Reference webpath.py docstrings for Examples sections and type hint patterns
- Reference __init__.py module-level documentation for package overview style
- Use AssetReference, TraversableElement, and RelativePathStrategy docstrings as templates
- Follow _walk_tree and make_path_nodes documentation patterns for helper functions

**Example components from examples/mysite**

- Use Heading component as basis for documentation examples
- Reference mysite package structure for realistic component organization
- Show static asset references (CSS, JS) using existing component patterns
- Demonstrate package structure with __init__.py files

**Type hint and validation patterns**

- Use Protocol definitions like RenderStrategy as examples of extensibility
- Show TypeGuard usage from _should_process_href for type narrowing
- Demonstrate dataclass patterns from AssetReference and RelativePathStrategy
- Include frozen=True, slots=True optimization patterns in documentation

**Documentation tooling already in dependencies**

- Use Sphinx (furo theme) for documentation generation
- Use myst-parser for Markdown support in Sphinx
- Use linkify-it-py for automatic URL linking
- Reference pytest-benchmark for performance documentation section

## Out of Scope

- Automated API reference generation from docstrings (write manually following patterns)
- Interactive examples or live code playgrounds
- Video tutorials or screencasts
- PDF or ePub format exports
- Versioned documentation (only current version)
- Search functionality beyond GitHub's built-in search
- Comments or discussion features on documentation
- Analytics or usage tracking on documentation site
- Automated link checking or broken link detection
- Documentation translations to other languages

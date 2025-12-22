# Spec Requirements: Documentation and Examples

## Initial Description

Write comprehensive API documentation with type signatures, create cookbook with common patterns (component libraries, theme development, SSG builds), and build example projects demonstrating dynamic and static workflows. Include migration guides from framework-specific approaches.

## Requirements Discussion

### First Round Questions

**Q1:** For API documentation, should I follow the style of your current docstrings (with type hints shown in the signatures) or would you prefer a different format?
**Answer:** Use the format in the current docstrings plus the type hints

**Q2:** For the "Getting Started" section, should I create a minimal example or show a more complete setup with multiple components?
**Answer:** Just basic examples for Getting Started

**Q3:** For the cookbook, I'm thinking these patterns would be most useful: (a) building component libraries with colocated assets, (b) creating portable themes, (c) SSG integration with asset collection, (d) migrating from framework-specific helpers. Should we include all of these?
**Answer:** Yes to the cookbook patterns: (a) building component libraries with colocated assets, (b) creating portable themes, (c) SSG integration with asset collection, (d) migrating from framework-specific helpers

**Q4:** For example projects, should I create separate examples for Flask, Django, FastAPI (dynamic servers) and Sphinx, Pelican (SSGs), or would you prefer focusing on one or two?
**Answer:** Create Flask/Django/FastAPI set of examples, plus Sphinx too

**Q5:** For the documentation site itself, should it be deployed to GitHub Pages? If so, should I copy the GitHub Actions workflow setup from ../storyville?
**Answer:** GitHub Pages for hosting. Copy the .github setup from ../storyville

**Q6:** I'm assuming the documentation structure should have: Overview, Installation, Getting Started, API Reference, Cookbook, Examples, Migration Guides. Should the README also have these sections (but with more terse examples)?
**Answer:** Yes to the documentation structure AND have corresponding sections in the README (but with much more terse examples). Add a Key Features section based on all the specs we have written

**Q7:** Should we include diagrams explaining the path rewriting lifecycle (make_path → make_path_nodes → render_path_nodes) and the relationship between these functions?
**Answer:** Yes, include diagrams explaining the path rewriting lifecycle, the relationship between make_path() → make_path_nodes() → render_path_nodes(), and how relative path calculation works

**Q8:** Is there anything you specifically DON'T want documented or any features you want to exclude from the examples?
**Answer:** No exclusions - document everything that exists

### Existing Code to Reference

**Similar Features Identified:**
- Documentation site setup from: `/Users/pauleveritt/projects/t-strings/storyville/.github/workflows/`
  - `pages.yml`: GitHub Pages deployment workflow
  - `ci.yml`: CI testing workflow pattern
  - `actions/setup-python-uv/action.yml`: Composite action for Python/uv setup

**Components to reference:**
- Storyville's GitHub workflows for CI and Pages deployment patterns
- Storyville's composite action pattern for reusable Python/uv setup

**Backend logic to reference:**
- Existing docstring style from `src/tdom_path/tree.py`, `src/tdom_path/webpath.py`, `src/tdom_path/__init__.py`
- Type hint patterns and example structures used throughout the codebase

### Follow-up Questions

**Follow-up 1:** For the diagrams explaining the lifecycle and relationships, what format would you prefer? Should I create:
- ASCII/text-based diagrams in the markdown (simple, always renders)
- Mermaid diagrams (GitHub renders these natively in markdown)
- SVG/PNG image files (most professional looking but requires separate files)
- A combination (e.g., Mermaid in docs, ASCII in README for simplicity)

**Answer:** Use Mermaid diagrams for explaining lifecycle and relationships

**Follow-up 2:** Looking at the Storyville setup, they use Python 3.14t (free-threaded). Should the tdom-path documentation build use the same Python version and setup, or should it use a more stable/standard Python version for broader compatibility?

**Answer:** Build the docs using Python 3.14.2 (not 3.14.2t - the free-threaded version)

**Follow-up 3:** For the Key Features section in the README, should I derive these directly from the Product Mission's "Key Features" section, or should I create a more code-focused list based on what's actually implemented in the completed specs?

**Answer:** Derive Key Features from completed specs (not the Product Mission's Key Features)

## Visual Assets

### Files Provided:
No visual files found in the visuals folder.

### Visual Insights:
No visual assets provided.

## Requirements Summary

### Functional Requirements

**Documentation Structure:**
- Overview/Why section explaining the purpose and benefits
- Installation instructions
- Quick Start with basic examples
- Core Concepts explaining key abstractions
- Comprehensive API Reference with type signatures and current docstring style
- Cookbook/Patterns section with:
  - Building component libraries with colocated assets
  - Creating portable themes
  - SSG integration with asset collection
  - Migration from framework-specific helpers
- Framework Integration Guides for Flask, Django, FastAPI, and Sphinx
- Migration Guides from framework-specific approaches

**Diagrams:**
- Mermaid diagrams explaining:
  - Path rewriting lifecycle
  - Function relationships (make_path() → make_path_nodes() → render_path_nodes())
  - Relative path calculation mechanism

**Example Projects:**
- Flask example demonstrating dynamic server usage
- Django example demonstrating dynamic server usage
- FastAPI example demonstrating dynamic server usage
- Sphinx example demonstrating SSG usage

**README Sections:**
- Key Features (derived from completed specs, not Product Mission)
- Terse versions of all documentation sections
- Quick examples without extensive explanation

**Documentation Build:**
- Use Python 3.14.2 (standard version, not free-threaded 3.14.2t)
- Deploy to GitHub Pages
- Copy GitHub Actions workflow setup from ../storyville

**API Documentation Format:**
- Follow existing docstring style from codebase
- Include type hints in signatures
- Document all existing features without exclusions

### Reusability Opportunities

**GitHub Workflows to Copy:**
- `storyville/.github/workflows/pages.yml` for GitHub Pages deployment
- `storyville/.github/workflows/ci.yml` for CI testing patterns
- `storyville/.github/actions/setup-python-uv/action.yml` for reusable Python/uv setup

**Docstring Style References:**
- `src/tdom_path/tree.py` for type hint and documentation patterns
- `src/tdom_path/webpath.py` for API documentation style
- `src/tdom_path/__init__.py` for module-level documentation

### Scope Boundaries

**In Scope:**
- Complete API reference documentation
- All core concepts and abstractions
- Cookbook patterns for common use cases
- Framework integration examples (Flask, Django, FastAPI, Sphinx)
- Migration guides from framework-specific approaches
- Mermaid diagrams for lifecycle and relationships
- GitHub Pages deployment setup
- Corresponding README sections with terse examples
- Key Features section derived from completed specs

**Out of Scope:**
- No exclusions - document everything that currently exists in the codebase

### Technical Considerations

**Build Environment:**
- Python 3.14.2 (standard version, not free-threaded)
- uv for dependency management (following storyville pattern)
- GitHub Actions for CI and deployment

**Documentation Tools:**
- Mermaid for diagrams (native GitHub rendering)
- GitHub Pages for hosting
- Type hints visible in all API signatures

**Integration Points:**
- Copy and adapt GitHub Actions workflows from storyville
- Reference existing docstring patterns from codebase
- Examples must demonstrate both dynamic (Flask/Django/FastAPI) and static (Sphinx) workflows

**Content Sources:**
- Derive Key Features from completed specs rather than Product Mission
- Use actual codebase implementations as source of truth
- Include all implemented features without exclusions

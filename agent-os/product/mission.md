# Product Mission

## Pitch

tdom-path is a Python library that helps web developers building framework-portable themes and components manage static
asset paths and links by providing intelligent path rewriting that works with `Node` structures, enabling local asset
organization with excellent IDE support while supporting both dynamic servers and static site generators.

## Users

### Primary Customers

- **Python Theme Developers**: Developers creating reusable, portable themes across multiple web frameworks (Django,
  Flask, FastAPI, Sphinx, Pelican)
- **Component Library Authors**: Developers building component ecosystems that need to work across different Python web
  frameworks
- **Build Tool Developers**: Developers creating static site generators and asset build pipelines that need
  framework-agnostic path resolution

### User Personas

**Full-Stack Python Developer** (25-45 years)

- **Role:** Building web applications and documentation sites using various Python frameworks
- **Context:** Works on multiple projects using different frameworks (Django for apps, Sphinx for docs); wants to reuse
  themes and components across projects
- **Pain Points:** Framework-specific path helpers (url_for, static tags) lock them into one ecosystem; moving static
  assets breaks IDE autocomplete and refactoring; debugging path issues wastes hours
- **Goals:** Write components once, use them everywhere; get IDE support for asset paths; catch broken links at build
  time instead of runtime

**Theme/Component Library Maintainer** (28-50 years)

- **Role:** Maintains open-source or internal theme libraries used across multiple projects
- **Context:** Needs themes to work in both dynamic (Flask/Django) and static (Sphinx/Pelican) contexts; wants to ship
  self-contained components with assets
- **Pain Points:** Can't colocate assets with component code; framework-specific syntax prevents portability; users
  struggle with asset path configuration
- **Goals:** Ship components with assets bundled together; provide great DX with autocomplete and static analysis;
  support both SSG and dynamic server workflows

**Tooling Developer** (30-55 years)

- **Role:** Building static site generators, build tools, or developer experience tooling
- **Context:** Creating the next generation of Python web tooling; wants to leverage modern Python features (t-strings,
  free-threading)
- **Pain Points:** Existing path systems require multiple parse/stringify cycles; can't provide good error messages;
  hard to integrate with modern Python tooling
- **Goals:** Build performant, type-safe path handling; provide excellent error messages through static analysis; create
  pluggable architecture for extensibility

## The Problem

### Path Management Breaks Portability and Developer Experience

Current Python web frameworks solve path resolution through framework-specific helpers (Django's `static` template tag,
Flask's `url_for`, Jinja2's custom filters). This approach creates several critical problems:

1. **Ecosystem Fragmentation**: Themes and components written for one framework cannot be reused in another without
   significant rewrites, preventing the emergence of a "big ecosystem of quality, interoperable themes, components, and
   tooling."

2. **Poor Developer Experience**: Framework-specific syntax like `url_for('static', filename='styles.css')` defeats IDE
   tooling. Developers lose autocomplete, go-to-definition, refactoring support, and error detection that would work
   with actual file paths.

3. **Asset Organization Chaos**: Best practices force static assets into centralized directories rather than colocating
   them with components, making code harder to understand, maintain, and package.

4. **Build System Complexity**: Systems that work for dynamic servers (Django/Flask) don't translate to static site
   generators (Sphinx/Pelican), requiring parallel implementations and multiple parse/stringify cycles.

5. **Limited Error Detection**: Path errors typically surface at runtime rather than build time, and error messages
   provide little context about what went wrong or how to fix it.

**Our Solution:** tdom-path enables developers to write actual file paths (`./static/styles.css`) that work with IDE
tooling, then rewrites these paths relative to render targets at the appropriate lifecycle stage. By operating on `Node`
structures rather than strings and using Python's `PurePath` interface, we provide framework portability, excellent DX,
and optimized performance suitable for both dynamic and static workflows.

## Differentiators

### Native Python Path Semantics with IDE Support

Unlike Flask's `url_for()` or Django's template tags which use framework-specific strings, we leverage actual file paths
that IDEs understand natively. This results in autocomplete, error squiggles for broken paths, go-to-definition support,
and automatic refactoring when files are renamed—developer experience improvements that are impossible with magic
strings.

### Node-Based Optimization

Unlike WSGI middleware or template post-processors that parse HTML strings multiple times, we operate directly on `Node`
structures during the rendering lifecycle. This results in single-pass path resolution without repeated parse/stringify
cycles, and enables collecting component metadata during construction for optimized build output.

### Framework-Portable by Design

Unlike framework-specific solutions tied to Django, Flask, Sphinx, or Pelican, we provide a Protocol-based architecture
that works identically across dynamic servers and static site generators. This results in true theme portability—write
once, deploy anywhere—fulfilling the vision of a unified Python web component ecosystem.

### Context-Aware Lifecycle Integration

Unlike simplistic string replacement approaches, we integrate with the full rendering lifecycle through a context object
pattern. This results in path resolution that can happen at definition time (component creation), application time (
route rendering), or build time (SSG output), with appropriate strategies for each stage.

### Static Analysis Friendly

Unlike "convention over configuration" approaches that rely on runtime discovery, we use declarative, type-safe patterns
that static analysis tools can understand. This results in early error detection through linters and type checkers,
better IDE support, and the ability to validate links before deployment.

## Key Features

### Core Features

- **Actual Path References:** Write `./static/styles.css` as real file paths that IDEs can autocomplete, validate, and
  refactor automatically, rather than framework-specific magic strings
- **Node-Based Path Rewriting:** Transform paths directly in `Node` structures without parsing HTML strings, eliminating
  redundant parse/stringify cycles and enabling single-pass optimization
- **Relative Path Resolution:** Calculate paths relative to render targets, supporting both dynamic server URLs and
  static file output directories without framework-specific helpers
- **PurePath Interface:** Leverage Python's familiar `PurePath` API for path operations, providing type safety and
  tooling integration while supporting custom path tree implementations

### Portability Features

- **Framework-Agnostic Design:** Work identically across Django, Flask, FastAPI (dynamic) and Sphinx, Pelican (static)
  without framework-specific code, enabling true theme portability
- **Protocol-Based Architecture:** Define path resolution through Python Protocols, allowing frameworks to provide
  custom implementations while maintaining consistent interfaces
- **Component Colocation:** Keep static assets in component directories (`header/static/styles.css`) rather than
  centralized locations, making components truly self-contained and portable

### Build System Features

- **Lifecycle-Aware Resolution:** Resolve paths at the appropriate stage (definition time, application time, or build
  time) based on context and requirements
- **Site Prefix Support:** Handle SSG deployment prefixes automatically, ensuring paths work correctly whether deployed
  to root or a subdirectory
- **Static and Dynamic Links:** Rewrite both static asset paths (`<link>`, `<script>`, `<img>`) and navigation links (
  `<a href>`) with appropriate strategies for each
- **Build Metadata Collection:** Gather component path information during rendering for optimized asset processing and
  build output generation

### Developer Experience Features

- **Static Analysis Support:** Enable linters, type checkers, and IDE inspections to validate paths before runtime,
  catching broken references during development
- **Rich Error Messages:** Provide context-rich error messages that explain what went wrong and how to fix it, going
  beyond generic tracebacks
- **Link Validation:** Detect broken links and missing assets at build time (especially for SSGs), preventing deployment
  of broken references
- **Free-Threading Friendly:** Design render context as immutable system data plus per-render bags optimized for
  concurrent rendering in free-threaded Python

### Advanced Features

- **ChainMap Context Pattern:** Separate immutable system context from mutable per-render context using `ChainMap`,
  enabling efficient context reuse across renders
- **Component Annotations:** Store component metadata (path on disk, static assets) in `Node` annotations, preserving
  information through the rendering pipeline
- **Pluggable Implementations:** Register custom path resolution strategies through Protocol-based service architecture,
  supporting specialized workflows and optimizations
- **t-String Integration:** Work seamlessly with template strings as first-class Python features, enabling compile-time
  optimizations and better tooling integration

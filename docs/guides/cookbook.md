# Cookbook Patterns

This guide provides practical patterns for common use cases with tdom-path.

## Building Component Libraries

Component libraries benefit from colocated assets - keeping CSS, JS, and other resources alongside component code.

### Component Structure

```
mysite/
  components/
    heading/
      __init__.py
      heading.py
      static/
        heading.css
        heading.js
```

### Component Implementation

```python
>>> # mysite/components/heading/heading.py
>>> from tdom import Element
>>> from tdom_path import path_nodes
>>> class Heading:
...     def __init__(self, text: str):
...         self.text = text
...
...     @path_nodes
...     def __html__(self) -> Element:
...         return Element("div", {"class": "heading"}, children=[
...             Element("head", children=[
...                 Element("link", {
...                     "rel": "stylesheet",
...                     "href": "static/heading.css"
...                 }),
...                 Element("script", {"src": "static/heading.js"}),
...             ]),
...             Element("h1", children=[self.text]),
...         ])
```

### Package Entry Point

```python
>>> # mysite/components/heading/__init__.py
>>> from mysite.components.heading.heading import Heading  # doctest: +SKIP
>>> __all__ = ["Heading"]  # doctest: +SKIP
```

### Usage

```python
>>> from mysite.components.heading import Heading
>>> # Component automatically resolves its own assets
>>> heading = Heading("Welcome")
>>> tree = heading.__html__()  # doctest: +SKIP
>>> # Assets are resolved relative to the heading module
```

### Benefits

- **Colocated Assets** - CSS and JS live with component code
- **Portable Components** - Components work anywhere they're imported
- **Type Safety** - Asset paths validated at build time
- **Framework Independence** - No framework-specific helpers needed

## Creating Portable Themes

Themes package reusable styling and assets that work across different frameworks.

### Theme Structure

```
mytheme/
  __init__.py
  base.py
  static/
    css/
      base.css
      components.css
    js/
      theme.js
  components/
    layout.py
    navigation.py
```

### Theme Base Component

```python
>>> # mytheme/base.py
>>> from tdom import Element
>>> from tdom_path import path_nodes
>>> class ThemeBase:
...     @path_nodes
...     def __html__(self) -> Element:
...         return Element("head", children=[
...             # Theme assets using package paths
...             Element("link", {
...                 "rel": "stylesheet",
...                 "href": "mytheme:static/css/base.css"
...             }),
...             Element("link", {
...                 "rel": "stylesheet",
...                 "href": "mytheme:static/css/components.css"
...             }),
...             Element("script", {"src": "mytheme:static/js/theme.js"}),
...         ])
```

### Using the Theme

```python
>>> from mytheme import ThemeBase  # doctest: +SKIP
>>> from tdom_path import make_path_nodes, render_path_nodes
>>> from pathlib import PurePosixPath
>>> # Theme works in any web framework
>>> theme = ThemeBase()  # doctest: +SKIP
>>> tree = theme.__html__()  # doctest: +SKIP
>>> # Assets resolved via package paths
>>> target = PurePosixPath("templates/index.html")
>>> rendered = render_path_nodes(tree, target)  # doctest: +SKIP
>>> html_output = str(rendered)  # doctest: +SKIP
```

### Benefits

- **Framework Independence** - Same theme works in any web framework
- **Package Distribution** - Distribute themes as Python packages
- **Asset Bundling** - All theme assets packaged together
- **No Framework Lock-in** - Switch frameworks without rewriting themes

## SSG Integration Pattern

Static Site Generators (SSGs) need to collect and copy all assets during build. tdom-path provides `RelativePathStrategy.collected_assets` for this use case.

### Asset Collection During Build

```python
>>> from pathlib import PurePosixPath, Path
>>> from tdom_path import make_path_nodes, render_path_nodes
>>> from tdom_path.tree import RelativePathStrategy
>>> # Create strategy to collect assets
>>> strategy = RelativePathStrategy()
>>> # Render multiple pages
>>> pages = [  # doctest: +SKIP
...     ("index.html", index_component),
...     ("about.html", about_component),
...     ("contact.html", contact_component),
... ]
>>> for filename, component in pages:  # doctest: +SKIP
...     tree = component.__html__()
...     path_tree = make_path_nodes(tree, component)
...
...     target = PurePosixPath(f"build/{filename}")
...     rendered = render_path_nodes(path_tree, target, strategy=strategy)
...
...     # Write rendered HTML
...     Path(target).write_text(str(rendered))
>>> # After rendering all pages, copy collected assets
>>> build_dir = Path("build")
>>> for asset_ref in strategy.collected_assets:  # doctest: +SKIP
...     # asset_ref.source is Traversable for reading
...     # asset_ref.module_path is PurePosixPath for destination
...     dest_path = build_dir / asset_ref.module_path
...     dest_path.parent.mkdir(parents=True, exist_ok=True)
...     dest_path.write_bytes(asset_ref.source.read_bytes())
```

### Benefits

- **Automatic Asset Discovery** - No manual asset lists needed
- **Deduplication** - AssetReference uses frozen dataclass for set-based dedup
- **Build-Time Copying** - Copy assets only after all pages rendered
- **Complete Asset Manifest** - collected_assets contains all referenced assets

## Advanced Patterns

### Using @path_nodes Decorator

The decorator automatically applies `make_path_nodes()` to component output:

```python
>>> from tdom import Element
>>> from tdom_path import path_nodes
>>> # Function component
>>> @path_nodes  # doctest: +SKIP
... def heading(text: str) -> Element:
...     return Element("div", children=[
...         Element("link", {"href": "static/styles.css"}),
...         Element("h1", children=[text]),
...     ])
>>> # Class component with __call__
>>> class HeadingCallable:  # doctest: +SKIP
...     @path_nodes
...     def __call__(self) -> Element:
...         return Element("link", {"href": "static/styles.css"})
>>> # Class component with __html__
>>> class HeadingHTML:  # doctest: +SKIP
...     @path_nodes
...     def __html__(self) -> Element:
...         return Element("link", {"href": "static/styles.css"})
```

### Mixing Package and Relative Paths

Use both package paths and relative paths in the same component:

```python
>>> class Component:  # doctest: +SKIP
...     @path_nodes
...     def __html__(self) -> Element:
...         return Element("head", children=[
...             # Package path - from installed package
...             Element("link", {
...                 "rel": "stylesheet",
...                 "href": "bootstrap:dist/css/bootstrap.css"
...             }),
...             # Relative path - from component's module
...             Element("link", {
...                 "rel": "stylesheet",
...                 "href": "static/component.css"
...             }),
...             # Another package
...             Element("script", {"src": "jquery:dist/jquery.min.js"}),
...             # Local script
...             Element("script", {"src": "static/component.js"}),
...         ])
```

### Validating Assets with Fail-Fast

Asset validation happens automatically during `make_path_nodes()`:

```python
>>> from mysite.components.heading import Heading
>>> from tdom_path import make_path_nodes
>>> try:
...     tree = Element("link", {"href": "static/missing.css"})
...     make_path_nodes(tree, Heading)
... except FileNotFoundError as e:
...     # Error includes:
...     # - Asset filename: 'missing.css'
...     # - Attribute name: 'href'
...     # - Component name: 'Component'
...     # - Module context: 'mysite.components.component'
...     # - Full path for debugging
...     assert "missing.css" in str(e)
```

Benefits:
- Build-time error detection
- Clear error messages with context
- Prevents broken links in production
- Immediate feedback during development

### Custom RenderStrategy for CDN

Implement custom rendering strategies for CDN or absolute URLs:

```python
>>> from pathlib import PurePosixPath
>>> from importlib.resources.abc import Traversable
>>> from tdom_path.tree import RenderStrategy
>>> class CDNStrategy:
...     """Render all paths as CDN URLs."""
...
...     def __init__(self, cdn_base: str):
...         self.cdn_base = cdn_base.rstrip("/")
...
...     def calculate_path(self, source: Traversable, target: PurePosixPath) -> str:
...         # Convert Traversable to path string
...         path_str = str(source)
...         # Return CDN URL
...         return f"{self.cdn_base}/{path_str}"
>>> # Use custom strategy
>>> cdn_strategy = CDNStrategy("https://cdn.example.com")
>>> rendered = render_path_nodes(path_tree, target, strategy=cdn_strategy)  # doctest: +SKIP
>>> # Assets now point to: https://cdn.example.com/mysite/components/heading/static/styles.css
```

### Absolute Path Strategy

```python
>>> class AbsolutePathStrategy:
...     """Render all paths as absolute URLs from site root."""
...
...     def calculate_path(self, source: Traversable, target: PurePosixPath) -> str:
...         # Always return path from site root
...         return f"/{source}"
>>> # Use absolute path strategy
>>> absolute_strategy = AbsolutePathStrategy()
>>> rendered = render_path_nodes(path_tree, target, strategy=absolute_strategy)  # doctest: +SKIP
>>> # Assets now point to: /mysite/components/heading/static/styles.css
```

## Best Practices

1. **Colocate Assets** - Keep CSS/JS with component code
2. **Use Package Paths** - For third-party assets (bootstrap, jquery, etc.)
3. **Use Relative Paths** - For component-local assets
4. **Validate Early** - Let fail-fast validation catch errors during development
5. **Collect Assets for SSG** - Use RelativePathStrategy.collected_assets for build tools
6. **Framework Independence** - Write components once, use everywhere
7. **Type Safety** - Leverage type hints for IDE support and type checking

## Next Steps

- Review [API Reference](../reference/api-reference.md) for detailed function signatures
- See [Core Concepts](core-concepts.md) for deeper understanding of the lifecycle

# Framework Integration Guide

This guide demonstrates how to integrate tdom-path with popular Python web frameworks and static site generators.

## Flask Integration

Flask is a lightweight WSGI web framework. tdom-path integrates seamlessly with Flask routes and templates.

### Basic Setup

```python
# app.py
from flask import Flask
from pathlib import PurePosixPath
from tdom import Element
from tdom_path import make_path_nodes, render_path_nodes
from mysite.components.heading import Heading

app = Flask(__name__)

@app.route("/")
def index():
    # Create component
    heading = Heading("Welcome to Flask")
    tree = heading.__html__()

    # Transform asset paths
    path_tree = make_path_nodes(tree, heading)

    # Render for target page
    target = PurePosixPath("templates/index.html")
    rendered = render_path_nodes(path_tree, target)

    return str(rendered)

if __name__ == "__main__":
    app.run(debug=True)
```

### Component with Static Assets

```python
# mysite/components/heading/heading.py
from tdom import Element
from tdom_path import path_nodes

class Heading:
    def __init__(self, text: str):
        self.text = text

    @path_nodes
    def __html__(self) -> Element:
        return Element("html", children=[
            Element("head", children=[
                Element("link", {
                    "rel": "stylesheet",
                    "href": "static/heading.css"
                }),
                Element("script", {"src": "static/heading.js"}),
            ]),
            Element("body", children=[
                Element("h1", children=[self.text]),
            ]),
        ])
```

### Directory Structure

```
myflask/
  app.py
  mysite/
    components/
      heading/
        __init__.py
        heading.py
        static/
          heading.css
          heading.js
  templates/
    index.html
```

### Benefits

- **No Flask-Specific Helpers** - No need for `url_for()`
- **Type-Safe Components** - Components are pure Python
- **Asset Validation** - Assets validated at build time
- **Framework Portability** - Components work in other frameworks

## Django Integration

Django is a full-featured web framework. tdom-path works with Django views and templates.

### Basic Setup

```python
# myapp/views.py
from django.http import HttpResponse
from pathlib import PurePosixPath
from tdom_path import make_path_nodes, render_path_nodes
from mysite.components.heading import Heading

def index(request):
    # Create component
    heading = Heading("Welcome to Django")
    tree = heading.__html__()

    # Transform asset paths
    path_tree = make_path_nodes(tree, heading)

    # Render for target page
    target = PurePosixPath("myapp/templates/index.html")
    rendered = render_path_nodes(path_tree, target)

    return HttpResponse(str(rendered))
```

### URL Configuration

```python
# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
```

### Component Implementation

```python
# mysite/components/page/page.py
from tdom import Element
from tdom_path import path_nodes

class Page:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content

    @path_nodes
    def __html__(self) -> Element:
        return Element("html", children=[
            Element("head", children=[
                Element("title", children=[self.title]),
                Element("link", {
                    "rel": "stylesheet",
                    "href": "static/page.css"
                }),
            ]),
            Element("body", children=[
                Element("div", {"class": "container"}, children=[
                    Element("p", children=[self.content]),
                ]),
                Element("script", {"src": "static/page.js"}),
            ]),
        ])
```

### Directory Structure

```
mydjango/
  manage.py
  myapp/
    views.py
    urls.py
    templates/
      index.html
  mysite/
    components/
      page/
        __init__.py
        page.py
        static/
          page.css
          page.js
```

### Migration from Django Staticfiles

**Before:**
```python
# template.html
{% load static %}
<link rel="stylesheet" href="{% static 'myapp/style.css' %}">
```

**After:**
```python
# component.py
Element("link", {"rel": "stylesheet", "href": "static/style.css"})
```

### Benefits

- **No Template Tags** - No need for `{% static %}` template tag
- **Type Safety** - Components use Python type hints
- **Reusable Components** - Same components work outside Django
- **Build-Time Validation** - Asset errors caught before deployment

## FastAPI Integration

FastAPI is a modern async web framework. tdom-path works naturally with async routes.

### Basic Setup

```python
# main.py
from fastapi import FastAPI
from pathlib import PurePosixPath
from tdom import Element
from tdom_path import make_path_nodes, render_path_nodes
from mysite.components.heading import Heading

app = FastAPI()

@app.get("/")
async def index():
    # Create component
    heading = Heading("Welcome to FastAPI")
    tree = heading.__html__()

    # Transform asset paths
    path_tree = make_path_nodes(tree, heading)

    # Render for target page
    target = PurePosixPath("templates/index.html")
    rendered = render_path_nodes(path_tree, target)

    return {"html": str(rendered)}
```

### Component with Async Support

```python
# mysite/components/api_page/api_page.py
from tdom import Element
from tdom_path import path_nodes

class ApiPage:
    def __init__(self, title: str):
        self.title = title

    @path_nodes
    def __html__(self) -> Element:
        return Element("html", children=[
            Element("head", children=[
                Element("title", children=[self.title]),
                Element("link", {
                    "rel": "stylesheet",
                    "href": "static/api_page.css"
                }),
            ]),
            Element("body", children=[
                Element("div", {"id": "app"}, children=[
                    Element("h1", children=[self.title]),
                ]),
                Element("script", {"src": "static/api_page.js"}),
            ]),
        ])
```

### HTML Response

```python
from fastapi.responses import HTMLResponse

@app.get("/page", response_class=HTMLResponse)
async def page():
    api_page = ApiPage("API Documentation")
    tree = api_page.__html__()

    path_tree = make_path_nodes(tree, api_page)

    target = PurePosixPath("templates/page.html")
    rendered = render_path_nodes(path_tree, target)

    return str(rendered)
```

### Directory Structure

```
myfastapi/
  main.py
  mysite/
    components/
      api_page/
        __init__.py
        api_page.py
        static/
          api_page.css
          api_page.js
  templates/
    index.html
    page.html
```

### Benefits

- **Async Compatible** - Works with async routes
- **Type Safety** - FastAPI + tdom-path both use type hints
- **No Template Engine** - Direct HTML generation
- **Framework Independence** - Components work elsewhere

## Sphinx Integration

Sphinx is a documentation generator. tdom-path enables component-based documentation with asset collection for static builds.

### Sphinx Configuration

```python
# docs/conf.py
from pathlib import PurePosixPath, Path
from tdom_path import make_path_nodes, render_path_nodes
from tdom_path.tree import RelativePathStrategy

# Enable MyST parser for Markdown
extensions = [
    'myst_parser',
    'sphinxcontrib.mermaid',
]

def collect_component_assets(app, exception):
    """Collect and copy component assets after build."""
    if exception:
        return

    # Create strategy to collect assets
    strategy = RelativePathStrategy()

    # Import and render your components
    # (This example shows the pattern - adapt to your structure)
    from mysite.components.doc_example import DocExample

    component = DocExample()
    tree = component.__html__()
    path_tree = make_path_nodes(tree, component)

    target = PurePosixPath("_build/html/index.html")
    rendered = render_path_nodes(path_tree, target, strategy=strategy)

    # Copy all collected assets to build output
    build_dir = Path(app.outdir)
    for asset_ref in strategy.collected_assets:
        dest_path = build_dir / asset_ref.module_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(asset_ref.source.read_bytes())

def setup(app):
    """Register Sphinx event handlers."""
    app.connect("build-finished", collect_component_assets)
```

### Component for Documentation

```python
# mysite/components/doc_example/doc_example.py
from tdom import Element
from tdom_path import path_nodes

class DocExample:
    @path_nodes
    def __html__(self) -> Element:
        return Element("div", {"class": "example"}, children=[
            Element("link", {
                "rel": "stylesheet",
                "href": "static/example.css"
            }),
            Element("div", {"class": "demo"}, children=[
                Element("p", children=["This is a live component example."]),
            ]),
            Element("script", {"src": "static/example.js"}),
        ])
```

### Using Components in Markdown

```markdown
# Component Examples

Here's a live example of our component:

{eval-rst}
.. raw:: html

   <!-- Embed rendered component here -->

{/eval-rst}
```

### Asset Collection Pattern

```python
# Build script or Sphinx extension
from pathlib import PurePosixPath, Path
from tdom_path.tree import RelativePathStrategy

# Render all documentation pages
strategy = RelativePathStrategy()

for doc_file in doc_files:
    # Render component for each doc page
    component = load_component(doc_file)
    tree = component.__html__()
    path_tree = make_path_nodes(tree, component)

    target = PurePosixPath(f"_build/html/{doc_file}")
    rendered = render_path_nodes(path_tree, target, strategy=strategy)

# After all pages rendered, copy assets
build_dir = Path("_build/html")
for asset_ref in strategy.collected_assets:
    dest_path = build_dir / asset_ref.module_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(asset_ref.source.read_bytes())
```

### Directory Structure

```
docs/
  conf.py
  index.md
  examples/
    components.md
  mysite/
    components/
      doc_example/
        __init__.py
        doc_example.py
        static/
          example.css
          example.js
  _build/
    html/
```

### Benefits

- **Component-Based Docs** - Use components in documentation
- **Automatic Asset Collection** - No manual asset copying
- **Build-Time Rendering** - Fast static output
- **Consistent Styling** - Same components in docs and app

## Common Patterns Across Frameworks

### Basic Component Pattern

```python
from tdom import Element
from tdom_path import path_nodes

class Component:
    @path_nodes
    def __html__(self) -> Element:
        return Element("div", children=[
            Element("link", {"href": "static/component.css"}),
            Element("div", children=["Content"]),
        ])
```

### Rendering Pattern

```python
from pathlib import PurePosixPath
from tdom_path import make_path_nodes, render_path_nodes

# Create and transform
component = Component()
tree = component.__html__()
path_tree = make_path_nodes(tree, component)  # Usually not needed with @path_nodes

# Render for target
target = PurePosixPath("output/page.html")
rendered = render_path_nodes(path_tree, target)

# Convert to HTML string
html = str(rendered)
```

### Error Handling

```python
try:
    path_tree = make_path_nodes(tree, component)
except FileNotFoundError as e:
    # Asset not found - log or handle error
    logger.error(f"Asset validation failed: {e}")
    raise
```

## Framework Comparison

| Feature | Flask | Django | FastAPI | Sphinx |
|---------|-------|--------|---------|--------|
| **Integration Complexity** | Low | Medium | Low | Medium |
| **Async Support** | No | No | Yes | N/A |
| **Component Reuse** | Yes | Yes | Yes | Yes |
| **Asset Collection** | Manual | Manual | Manual | Automatic |
| **Type Safety** | Yes | Yes | Yes | Yes |

## Best Practices

1. **Use @path_nodes Decorator** - Automatic transformation
2. **Validate Assets Early** - Let fail-fast catch errors
3. **Collect Assets for SSG** - Use RelativePathStrategy.collected_assets
4. **Framework Independence** - Write components once
5. **Type Hints** - Leverage IDE support
6. **Error Handling** - Handle FileNotFoundError appropriately

## Troubleshooting

### Assets Not Found

```python
# Error: Asset not found
# Solution: Check asset path relative to component module
Element("link", {"href": "static/styles.css"})  # Correct
Element("link", {"href": "/static/styles.css"}) # Wrong - absolute path
```

### Relative Paths Incorrect

```python
# Ensure target path is correct module-relative path
target = PurePosixPath("mysite/pages/about.html")  # Correct
target = PurePosixPath("/about.html")             # Wrong - absolute
```

### External URLs Being Processed

```python
# External URLs are automatically skipped
Element("link", {"href": "https://cdn.example.com/style.css"})  # Not processed
Element("link", {"href": "//cdn.example.com/style.css"})        # Not processed
Element("link", {"href": "mailto:test@example.com"})             # Not processed
```

## Next Steps

- See [Cookbook Patterns](cookbook.md) for common use cases
- Review [API Reference](../reference/api-reference.md) for detailed documentation
- Explore [Core Concepts](core-concepts.md) for deeper understanding

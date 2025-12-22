# Flask Example - tdom-path Integration

This example demonstrates how to use tdom-path with Flask for dynamic server-side rendering with component-based asset management.

## Features Demonstrated

- Component rendering in Flask routes
- Colocated CSS and JS assets with components
- Automatic asset path resolution
- Relative path calculation for HTML output
- Both package paths and relative paths

## Project Structure

```
flask-example/
  app.py                    # Flask application entry point
  mysite/
    components/
      heading/
        __init__.py
        heading.py          # Heading component
        static/
          heading.css       # Component CSS
          heading.js        # Component JavaScript
```

## Setup

1. Ensure tdom-path is installed:
```bash
uv pip install tdom-path
```

2. Install Flask:
```bash
uv pip install flask
```

## Running the Example

```bash
# From this directory
python app.py
```

Then open your browser to `http://localhost:5000`

## How It Works

### Component Definition

The `Heading` component uses the `@path_nodes` decorator to automatically transform asset paths:

```python
from tdom import Element
from tdom_path import path_nodes

class Heading:
    @path_nodes
    def __html__(self) -> Element:
        return Element("html", children=[
            Element("head", children=[
                # Relative path - resolved to component's static directory
                Element("link", {
                    "rel": "stylesheet",
                    "href": "static/heading.css"
                }),
            ]),
            Element("body", children=[
                Element("h1", children=["Welcome to Flask!"]),
                Element("script", {"src": "static/heading.js"}),
            ]),
        ])
```

### Flask Route

The route renders the component and calculates relative paths:

```python
from pathlib import PurePosixPath
from tdom_path import render_path_nodes

@app.route("/")
def index():
    heading = Heading()
    tree = heading.__html__()

    # Render with relative paths
    target = PurePosixPath("templates/index.html")
    rendered = render_path_nodes(tree, target)

    return str(rendered)
```

### Asset Resolution

1. `@path_nodes` decorator transforms `href="static/heading.css"` to Traversable
2. `render_path_nodes()` calculates relative path from target to asset
3. Final HTML contains correct relative path to the asset

## Key Concepts

- **Colocated Assets** - CSS and JS live with component code
- **Automatic Path Resolution** - No need for Flask's `url_for()`
- **Type Safety** - Components are pure Python with type hints
- **Framework Independence** - Same component works in Django, FastAPI, etc.

## Extending This Example

Try these modifications:

1. Add more components (e.g., Footer, Navigation)
2. Use package paths for third-party assets (e.g., "bootstrap:dist/css/bootstrap.css")
3. Implement multiple routes with different components
4. Add error handling for missing assets

## Next Steps

- See [Flask Integration Guide](../../docs/guides/framework-integration.md#flask-integration)
- Explore [Cookbook Patterns](../../docs/guides/cookbook.md)
- Review [Core Concepts](../../docs/guides/core-concepts.md)

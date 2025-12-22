"""Flask application demonstrating tdom-path integration.

This example shows:
- Component rendering in Flask routes
- Colocated static assets with components
- Automatic asset path resolution
- Relative path calculation for HTML output
"""

from flask import Flask
from pathlib import PurePosixPath
from tdom_path import render_path_nodes
from mysite.components.heading import Heading

app = Flask(__name__)


@app.route("/")
def index():
    """Render index page with Heading component."""
    # Create component instance
    heading = Heading("Welcome to Flask with tdom-path!")

    # Get component tree (already transformed by @path_nodes decorator)
    tree = heading.__html__()

    # Render with relative paths for target location
    target = PurePosixPath("templates/index.html")
    rendered = render_path_nodes(tree, target)

    # Convert to HTML string and return
    return str(rendered)


@app.route("/about")
def about():
    """Render about page with Heading component."""
    heading = Heading("About This Example")
    tree = heading.__html__()

    # Different target path for about page
    target = PurePosixPath("templates/about.html")
    rendered = render_path_nodes(tree, target)

    return str(rendered)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

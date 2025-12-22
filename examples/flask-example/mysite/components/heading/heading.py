"""Heading component with colocated static assets."""

from tdom import Element
from tdom_path import path_nodes


class Heading:
    """A heading component with CSS and JS assets.

    This component demonstrates:
    - Colocated static assets (CSS, JS)
    - Automatic path resolution with @path_nodes decorator
    - Type-safe component definition
    """

    def __init__(self, text: str):
        """Initialize heading with text content.

        Args:
            text: The heading text to display
        """
        self.text = text

    @path_nodes
    def __html__(self) -> Element:
        """Render heading component as HTML.

        The @path_nodes decorator automatically transforms:
        - href="static/heading.css" -> Traversable instance
        - src="static/heading.js" -> Traversable instance

        Returns:
            Element tree with Traversable asset references
        """
        return Element(
            "html",
            attrs={"lang": "en"},
            children=[
                Element(
                    "head",
                    children=[
                        Element("meta", {"charset": "UTF-8"}),
                        Element(
                            "meta",
                            {
                                "name": "viewport",
                                "content": "width=device-width, initial-scale=1.0",
                            },
                        ),
                        Element("title", children=[self.text]),
                        # Relative path - resolved to component's static directory
                        Element(
                            "link", {"rel": "stylesheet", "href": "static/heading.css"}
                        ),
                    ],
                ),
                Element(
                    "body",
                    children=[
                        Element(
                            "div",
                            {"class": "heading-container"},
                            children=[
                                Element(
                                    "h1",
                                    {"class": "heading-title"},
                                    children=[self.text],
                                ),
                                Element(
                                    "p",
                                    {"class": "heading-description"},
                                    children=[
                                        "This heading component uses tdom-path for asset management."
                                    ],
                                ),
                            ],
                        ),
                        # Component JavaScript
                        Element("script", {"src": "static/heading.js"}),
                    ],
                ),
            ],
        )

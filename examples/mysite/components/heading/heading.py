"""Heading component with static CSS reference."""


class Heading:
    """A heading component that references a static stylesheet."""

    def __init__(self, text: str = "Hello World") -> None:
        """Initialize heading with text.

        Args:
            text: The heading text to display
        """
        self.text = text

    def __html__(self) -> str:
        """Return HTML representation with CSS link.

        Returns:
            HTML string with link to static stylesheet
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="./static/styles.css">
</head>
<body>
    <h1>{self.text}</h1>
</body>
</html>"""

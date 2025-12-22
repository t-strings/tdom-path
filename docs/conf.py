# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "tdom-path"
copyright = "2025, tdom-path contributors"
author = "tdom-path contributors"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings
extensions = [
    "myst_parser",  # MyST Markdown support
    "sphinx.ext.autodoc",  # API documentation from docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Link to other projects' documentation
    "sphinx.ext.todo",  # Support for to do items
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "sphinxcontrib.mermaid",  # Mermaid diagram support
]

# MyST configuration for Markdown support
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Napoleon settings for docstring parsing
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Use Furo theme
html_theme = "furo"
html_title = "tdom-path Documentation"
html_static_path = ["_static"]

# Theme options
html_theme_options = {
    "sidebar_hide_name": True,
    "light_logo": None,
    "dark_logo": None,
    "announcement": "<p>🚀 tdom-path: Component resource path utilities for web applications</p>",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_css_files = [
    "css/custom.css",
]

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "tdom-pathdoc"

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "letterpaper",
    # The font size ('10pt', '11pt' or '12pt').
    "pointsize": "10pt",
}

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "tdom-path", "tdom-path Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "tdom-path",
        "tdom-path Documentation",
        author,
        "tdom-path",
        "Component resource path utilities for web applications.",
        "Miscellaneous",
    ),
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
epub_identifier = "https://github.com/your-repo/tdom-path"

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]

# -- Intersphinx configuration -----------------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Autodoc configuration ---------------------------------------------------

# Automatically extract type hints when specified
autodoc_typehints = "description"

# Don't show class signature with the class' name
autodoc_class_signature = "separated"

# -- Todo extension configuration --------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Internationalization ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#internationalization

# Specifying the natural language of the text.
language = "en"

# -- Custom CSS -------------------------------------------------------------


def setup(app):
    """Add custom CSS for documentation."""
    app.add_css_file("css/custom.css")

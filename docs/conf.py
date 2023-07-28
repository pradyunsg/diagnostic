# -- General configuration ------------------------------------------------------------

extensions = [
    # first-party extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    # third-party extensions
    "myst_parser",
    "sphinxarg.ext",
]

# General information about the project.
project = "diagnostic"
copyright = "Pradyun Gedam, 2022"

# -- Options for HTML -----------------------------------------------------------------

html_theme = "furo"
html_title = project
html_static_path = ["_static"]

# -- Options for MyST-Parser ----------------------------------------------------------
#

myst_enable_extensions = ["deflist"]

# -- Options for Autodoc --------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

toc_object_entries_show_parents = "hide"
autodoc_preserve_defaults = True
autodoc_member_order = "bysource"

# Keep the type hints outside the function signature, moving them to the
# descriptions of the relevant function/methods.
autodoc_typehints = "description"

# Don't show the class signature with the class name.
autodoc_class_signature = "separated"

# Show all members of a class, even if they are undocumented.
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
}

# -- Options for Intersphinx -----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "rich": ("https://rich.readthedocs.io/en/stable/", None),
}

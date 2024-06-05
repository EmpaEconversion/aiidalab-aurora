# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Imports -----------------------------------------------------------------

import time
from aurora import __version__

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "AiiDAlab-Aurora"
author = "Edan Bainglass"
release = __version__

copyright_first_year = "2021"

copyright_owners = (
    "Loris Ercole (loris.ercole@gmail.com)",
    "Francisco F. Ramirez (francisco.ramirez@epfl.ch)",
    "Edan Bainglass (edan.bainglass@psi.ch)",
    "Giovanni Pizzi (giovanni.pizzi@psi.ch)",
)

current_year = str(time.localtime().tm_year)
copyright_year_string = current_year \
    if current_year == copyright_first_year \
    else f"{copyright_first_year}-{current_year}"

copyright = f"{copyright_year_string}. All rights reserved"

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = True

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_design",
]

# The pydata-sphinx-theme already loads the bootstrap css.
panels_add_bootstrap_css = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
# ~ master_doc = 'index'
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/images/full_logo.svg"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# Define common links
rst_epilog = """
.. _AiiDA: https://www.aiida.net
.. _AiiDAlab: https://www.aiidalab.net/
.. _tomato: https://dgbowl.github.io/tomato/master/index.html
.. _BIG-MAP App Store: https://big-map.github.io/big-map-registry/apps/aiidalab-aurora.html
"""

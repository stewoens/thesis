# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "py2cfg"
copyright = '2020, "Joe Studer <jmsxw4@mst.edu>", "Dr. Taylor <behindthebrain@zoho.eu>", "Kevin Lai <zlnh4@umsystem.edu>"'
author = '"Joe Studer <jmsxw4@mst.edu>", "Dr. Taylor <behindthebrain@zoho.eu>", "Kevin Lai <zlnh4@umsystem.edu>"'

# The full version, including alpha/beta/rc tags
release = "0.5.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "m2r2",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

from py2cfg.builder import CFGBuilder

cfg = CFGBuilder(short=True).build_from_file("fib", "../../examples/fib.py")
cfg.build_visual("fib_cfg", "svg", show=False, directory="_static")
cfg = CFGBuilder(short=True).build_from_file(
    "speed_sort", "../../examples/speed_sort.py"
)
cfg.build_visual("speed_sort_cfg", "svg", show=False, directory="_static")

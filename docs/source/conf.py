# -*- coding: utf-8 -*-
import subprocess
import sys
import sphinx.application
import pathlib

# -- Project information -----------------------------------------------------

project = "RJ RC Software"
copyright = "2022, Kevin Fu"
author = "Oswin So"

# The short X.Y version
version = ""
# The full version, including alpha/beta/rc tags
release = ""

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "breathe",
    "autoapi.extension",
]

# -- AutoAPI Configuration ---------------------------------------------------
# (Python-only auto-api generation)
# https://github.com/readthedocs/sphinx-autoapi
autoapi_type = 'python'
autoapi_dirs = ['../../rj_gameplay']

# -- Breathe Configuration ---------------------------------------------------
breathe_projects = {}
breathe_default_project = "rj_robocup"
breathe_default_members = (
    "members",
    "protected-members",
    "private-members",
    "undoc-members",
)

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {"collapse_navigation": False}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "custom.css",
]

html_logo = "_static/RoboBuzz.svg"

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "rj_robocupdoc"

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "rj_robocup.tex",
        "rj\\_robocup Documentation",
        "Oswin So",
        "manual",
    ),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "rj_robocup", "rj_robocup Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "rj_robocup",
        "rj_robocup Documentation",
        author,
        "rj_robocup",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


# -- Configuring standalone build ---------------------------------------------
def configure_doxyfile(
    input_dir: pathlib.Path,
    output_dir: pathlib.Path,
    doxyfile_dir: pathlib.Path,
) -> None:
    """Mimics the configure_file functionality in cmake.
    :param input_dir: Input directory for Doxygen.
    :param output_dir: Output directory for Doxygen.
    :param doxyfile_dir: The directory of the Doxyfile.
    """
    print("doxyfile_dir: {}".format(doxyfile_dir))
    try:
        with open(doxyfile_dir / "Doxyfile.in", "r") as file:
            filedata: str = file.read()
    except Exception as e:
        print(e)
        raise e

    print(1)
    filedata = filedata.replace("@DOXYGEN_INPUT_DIR@", str(input_dir))
    print(1)
    filedata = filedata.replace("@DOXYGEN_OUTPUT_DIR@", str(output_dir))

    print(3)
    with open(doxyfile_dir / "Doxyfile", "w") as file:
        file.write(filedata)


def run_doxygen(doxyfile_dir: pathlib.Path) -> None:
    """Runs the doxygen command in the passed in directory.
    :param doxyfile_dir: Path to the directory containing the Doxyfile.
    """
    subprocess.call("doxygen", shell=True, cwd=doxyfile_dir)


def generate_doxygen_xml(app: sphinx.application.Sphinx) -> None:
    """Generates the doxygen XML for breathe.
    :param app: Application object representing the Sphinx process
    """
    # Define all the paths.
    cwd = pathlib.Path().resolve()
    project_dir = cwd.parent

    input_dir = (project_dir / "soccer").resolve()
    output_dir = (cwd / "build").resolve()
    doxyfile_dir = (project_dir / "docs").resolve()

    # Configure the Doxyfile.
    configure_doxyfile(input_dir, output_dir, doxyfile_dir)

    # Run the doxygen command to generate the XML.
    run_doxygen(doxyfile_dir)

    # Update the "breathe_projects" variable so that the rj_robocup project points to the
    # correct directory.
    breathe_projects["rj_robocup"] = str((output_dir / "xml").resolve())


def setup(app: sphinx.application.Sphinx) -> None:
    """Adds generate_doxygen_xml hook to generate the doxygen XML for breathe.
    :param app: Application object representing the Sphinx process
    """
    app.connect("builder-inited", generate_doxygen_xml)

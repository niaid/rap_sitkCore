My Package Template Package
+++++++++++++++++++++++++++

The "My Package Template" project provides a skeleton structure for new Python packages and projects which contains
an advanced starting point for configuration and implementations for best practices for modern Python project
development. Github Actions are used to implement the following:
 - linting with `Black <https://black.readthedocs.io/en/stable/>`_, `flake8 <https://flake8.pycqa.org/en/latest/>`_ and `tufflehog <https://github.com/feeltheajf/truffleHog3>`_
 - testing with `pytest <https://docs.pytest.org]>`_
 - build `Sphinx <https://www.sphinx-doc.org/>`_ documentation and automatic updating `gh-pages` branch
 - build Python package as Github Action artifact
 - automatic release creation on git tags and uploading of Python packages


.. image:: https://github.com/niaid/rap_py_template/actions/workflows/main.yml/badge.svg?branch=master
   :target: https://github.com/niaid/rap_py_template/actions/workflows/main.yml
   :alt: Master Build Status


Sphinx docs: https://cautious-umbrella-90d21757.pages.github.io/
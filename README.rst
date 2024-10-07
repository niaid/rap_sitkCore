Radiomics Analysis Portal sitkCore
++++++++++++++++++++++++++++++++++

The sitkCore package used by the Radiomics Analysis Portal (`RAP`_) contains common utilities for developing image
analysis algorithms that use data provided by the Tuberculosis Portals Program (`TBPortals`_). The tools are written in
Python and provided as an installable Python package. The application programming interface (API) is documented in
Sphinx:
https://niaid.github.io/rap_sitkCore

.. image:: https://github.com/niaid/rap_sitkCore/actions/workflows/main.yml/badge.svg?branch=master
   :target: https://github.com/niaid/rap_sitkCore/actions/workflows/main.yml
   :alt: Main Build Status

Installation
------------

Dependencies are conventionally specified in `pyproject.toml`, and dependent packages are installed automatically by
`pip`_. The package can be directly installed from the Github with the following command::

    python -m pip install git+https://github.com/niaid/rap_sitkCore@v0.5.5


For pydicom to support more encodings additional pylibjpeg packages can be install. These dependencies are specified as
extra requirements in the setup.py. Specifying the package a "rap_sitkcore[pylibjpeg]" will install the extra packages.

Github Releases
^^^^^^^^^^^^^^^

The Python module is also distributed as a `wheel`_ binary package. Wheels from the master branch can be manually
downloaded from `Github Actions`_ in the "python-package" artifact.

Download the latest tagged release from the `Github Releases`_ page.


Contact
-------

Please use the `GitHub Issues`_ for support.

Additionally, we can be emailed at: bioinformatics@niaid.nih.gov Please include "rap_sitCore" in the subject line.

.. _RAP: https://rap.tbportals.niaid.nih.gov/
.. _TBPortals: https://tbportals.niaid.nih.gov/
.. _SimpleITK toolkit: https://simpleitk.org
.. _pip: https://pip.pypa.io/en/stable/quickstart/
.. _Github Actions: https://github.com/niaid/rap_sitkCore/actions?query=branch%3Amaster
.. _GitHub Issues:  https://github.com/niaid/rap_sitkCore
.. _wheel: https://www.python.org/dev/peps/pep-0427/
.. _Github Releases: https://github.com/niaid/rap_sitkCore/release
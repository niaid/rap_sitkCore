Radiomics Analysis Portal sitkCore
++++++++++++++++++++++++++++++++++

This sitkCore for the Radiomics Analysis Portal (RAP) contains common utilities for developing algorithms for analysis
of data from Tuberculosis Portals (TBPortals). The tools are written in Python and provided as an installable Python
package. The application programming interface (API) is documented in Sphinx: https://niaid.github.io/rap_sitkCore

.. image:: https://github.com/niaid/rap_sitkCore/actions/workflows/main.yml/badge.svg?branch=master
   :target: https://github.com/niaid/rap_sitkCore/actions/workflows/main.yml
   :alt: Master Build Status

Installation
------------

The Python module is distributed as a `wheel`_ binary package.

Dependencies are conventionally specified in `setup.py` and `requirements.txt`.

NIAID Artifactory
^^^^^^^^^^^^^^^^^

The `rap_sitkcore` package can be installed from the internal NIAID Python Package Index (PyPI) hosted on
artifactory with `pip`_. When this package is a dependency for other projects it can be automatically download from the
artifactory. The internal repository can be automatically used by setting an environment variable::

 PIP_EXTRA_INDEX_URL=https://{USERNAME}:{PASSWORD}@artifactory.niaid.nih.gov/artifactory/api/pypi/bcbb-pypi/simple

Then running::

 python -m pip install rap_sitkcore

Then the `rap_sitkcore` package can be installed if specified in another projects requirements.txt.

Github Releases
^^^^^^^^^^^^^^^

Wheels from the master branch can be manually download wheel from `Github Actions`_ in the "python-package" artifact.

Download the latest tagged release from the `Github Releases`_ page.

The wheel lists the package dependencies which are required for successful installation. This include internal NIAID
packages. If the internal "artifactory" repository is not configured then these additional dependencies will need to be
manually downloaded and installed before install `tbpcxr`. The downloaded wheels can be installed::

 python -m pip install rap_sitkcore-0.1-py3-none-any.whl


.. _pip: https://pip.pypa.io/en/stable/quickstart/
.. _Github Actions: https://github.com/niaid/rap_sitkCore/actions?query=branch%3Amaster
.. _GitHub Issues:  https://github.com/niaid/rap_sitkCore
.. _wheel: https://www.python.org/dev/peps/pep-0427/
.. _Github Releases: https://github.com/niaid/rap_sitkCore/release
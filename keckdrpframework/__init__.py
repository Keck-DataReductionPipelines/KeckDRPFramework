# Licensed under a 3-clause BSD style license - see LICENSE.rst

# Packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------

# Enforce Python version check during package import.
# This is the same check as the one at the top of setup.py
import sys

__minimum_python_version__ = "3.6.0"

__all__ = []


class UnsupportedPythonError(Exception):
    pass

min_version_tuple = tuple(map(int, __minimum_python_version__.split('.')))
current_version = sys.version_info[:3]

if current_version < min_version_tuple:
    raise UnsupportedPythonError(
        "keckdrpframework does not support Python < {}".format(__minimum_python_version__)
    )

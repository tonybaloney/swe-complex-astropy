# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This is a collection of monkey patches and workarounds for bugs in
earlier versions of Numpy.
"""

import warnings

import numpy as np

from astropy.utils import minversion
from astropy.utils.exceptions import AstropyDeprecationWarning

__all__ = [
    "COPY_IF_NEEDED",
    "NUMPY_LT_1_25",
    "NUMPY_LT_1_26",
    "NUMPY_LT_2_0",
    "NUMPY_LT_2_1",
    "NUMPY_LT_2_2",
    "NUMPY_LT_2_3",
    "NUMPY_LT_2_4",
    "NUMPY_LT_2_4_1",
    "NUMPY_LT_2_5",
    "chararray",
    "get_chararray",
]

# TODO: It might also be nice to have aliases to these named for specific
# features/bugs we're checking for (ex:
# astropy.table.table._BROKEN_UNICODE_TABLE_SORT)
NUMPY_LT_1_25 = not minversion(np, "1.25")
NUMPY_LT_1_26 = not minversion(np, "1.26")
NUMPY_LT_2_0 = not minversion(np, "2.0")
NUMPY_LT_2_1 = not minversion(np, "2.1.0.dev")
NUMPY_LT_2_2 = not minversion(np, "2.2.0.dev0")
NUMPY_LT_2_3 = not minversion(np, "2.3.0.dev0")
NUMPY_LT_2_4 = not minversion(np, "2.4.0.dev0")
NUMPY_LT_2_4_1 = not minversion(np, "2.4.1.dev0")
NUMPY_LT_2_5 = not minversion(np, "2.5.0.dev0")


COPY_IF_NEEDED = False if NUMPY_LT_2_0 else None


with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    from numpy.char import array as np_char_array
    from numpy.char import chararray as np_chararray


_deprecated_chararray_attributes = {
    "capitalize", "center", "count", "decode", "encode", "endswith",
    "expandtabs", "find", "index", "isalnum", "isalpha", "isdecimal",
    "isdigit", "islower", "isnumeric", "isspace", "istitle", "isupper",
    "join", "ljust", "lower", "lstrip", "replace", "rfind", "rindex",
    "rjust", "rpartition", "rsplit", "rstrip", "split", "splitlines",
    "startswith", "strip", "swapcase", "title", "translate", "upper",
    "zfill"
}  # fmt: skip


class chararray(np_chararray):
    """Version of np.char.chararray with deprecation warnings on special methods."""

    def __getattribute__(self, name):
        if name in _deprecated_chararray_attributes:
            warnings.warn(
                "chararray is deprecated, in future versions astropy will "
                "return a normal array so the special chararray methods "
                "(e.g., .rstrip()) will not be available. Use np.strings "
                "functions instead.",
                AstropyDeprecationWarning,
            )
        return super().__getattribute__(name)


def get_chararray(obj, itemsize=None, copy=True, unicode=None, order=None):
    """Get version of np.char.chararray that gives deprecation warnings on special methods."""
    return np_char_array(
        obj, itemsize=itemsize, copy=copy, unicode=unicode, order=order
    ).view(chararray)

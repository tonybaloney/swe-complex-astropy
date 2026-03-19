# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""This module contains helper functions handling metadata."""

import numpy as np

from .exceptions import MergeConflictError

__all__ = ["common_dtype"]


def dtype(arr):
    return getattr(arr, "dtype", np.dtype("O"))


def common_dtype(arrs):
    """
    Use numpy to find the common dtype for a list of ndarrays.

    Only allow arrays within the following fundamental numpy data types:
    ``np.bool_``, ``np.object_``, ``np.number``, ``np.character``, ``np.void``

    Parameters
    ----------
    arrs : list of ndarray
        Arrays for which to find the common dtype

    Returns
    -------
    dtype : numpy dtype
        Common dtype of the input arrays
    """
    np_types = (np.bool_, np.object_, np.number, np.character, np.void)
    uniq_types = {
        tuple(issubclass(dtype(arr).type, np_type) for np_type in np_types)
        for arr in arrs
    }
    if len(uniq_types) > 1:
        # Embed into the exception the actual list of incompatible types.
        incompat_types = [dtype(arr).name for arr in arrs]
        tme = MergeConflictError(f"Arrays have incompatible types {incompat_types}")
        tme._incompat_types = incompat_types
        raise tme

    return np.result_type(*[dtype(arr) for arr in arrs])

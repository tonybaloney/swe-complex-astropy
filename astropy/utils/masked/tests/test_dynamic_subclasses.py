# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Test importability and pickling of common Masked classes."""

import pickle

import numpy as np
import pytest

from astropy.coordinates.angles.core import Angle, Latitude, Longitude
from astropy.units.quantity import Quantity
from astropy.utils.masked import core


@pytest.mark.parametrize("base_class", [Quantity, Angle, Latitude, Longitude])
def test_importable(base_class):
    assert getattr(core, f"Masked{base_class.__name__}") is core.Masked(base_class)


@pytest.mark.parametrize("base_class", [Quantity, Angle, Latitude, Longitude])
def test_info_class_importable(base_class):
    """Regression test: info classes of Masked subclasses must be importable."""
    masked_cls = core.Masked(base_class)
    if "info" in masked_cls.__dict__:
        info_cls = type(masked_cls.__dict__["info"])
        assert getattr(core, info_cls.__name__) is info_cls


def test_pickle_masked_with_info():
    """Regression test for pickling Masked with initialized info (#19040, #18206)."""
    from astropy import units as u
    from astropy.table import QTable

    mq = core.Masked([1, 2, 3] * u.m, mask=[True, False, False])
    mq.info
    result = pickle.loads(pickle.dumps(mq))
    assert np.all(result.unmasked == mq.unmasked)
    assert np.all(result.mask == mq.mask)

    qt = QTable({"a": core.Masked([1, 2, 3] * u.m, mask=[True, False, False])})
    rt = pickle.loads(pickle.dumps(qt))
    assert np.all(rt["a"].unmasked == qt["a"].unmasked)
    assert np.all(rt["a"].mask == qt["a"].mask)

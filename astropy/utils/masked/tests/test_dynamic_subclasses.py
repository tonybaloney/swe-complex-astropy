# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Test importability of common Masked classes."""

import pickle

import pytest

from astropy.coordinates.angles.core import Angle, Latitude, Longitude
from astropy.units.quantity import Quantity
from astropy.utils.masked import core


@pytest.mark.parametrize("base_class", [Quantity, Angle, Latitude, Longitude])
def test_importable(base_class):
    assert getattr(core, f"Masked{base_class.__name__}") is core.Masked(base_class)


@pytest.mark.parametrize("base_class", [Quantity, Angle, Latitude, Longitude])
def test_info_class_importable(base_class):
    """Info classes for Masked subclasses should be importable for pickle support."""
    masked_cls = core.Masked(base_class)
    info_obj = masked_cls.__dict__.get("info")
    if info_obj is not None:
        info_cls = type(info_obj)
        assert getattr(core, info_cls.__name__) is info_cls


def test_pickle_masked_quantity_with_info():
    """Regression test: pickling Masked with initialized info should not raise."""
    import astropy.units as u

    mq = core.Masked([1, 2, 3] * u.m, mask=[True, False, False])
    mq.info  # Access info to trigger creation
    result = pickle.loads(pickle.dumps(mq))
    assert type(result) is type(mq)
    assert all(result.mask == mq.mask)


def test_pickle_masked_qtable():
    """Regression test for pickling Masked QTable (issues #19040, #18206)."""
    import astropy.units as u
    from astropy.table import QTable

    qt = QTable({"a": core.Masked([1, 2, 3] * u.m, mask=[True, False, False])})
    result = pickle.loads(pickle.dumps(qt))
    assert all(result["a"].mask == qt["a"].mask)

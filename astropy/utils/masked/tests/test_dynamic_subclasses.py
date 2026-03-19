# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Test importability and pickling of common Masked classes."""

import pickle

import astropy.units as u
import pytest

from astropy.coordinates.angles.core import Angle, Latitude, Longitude
from astropy.units.quantity import Quantity
from astropy.utils.masked import core
from astropy.utils.masked.core import Masked

BASE_CLASSES = [Quantity, Angle, Latitude, Longitude]


@pytest.mark.parametrize("base_class", BASE_CLASSES)
def test_importable(base_class):
    assert getattr(core, f"Masked{base_class.__name__}") is Masked(base_class)


@pytest.mark.parametrize("base_class", BASE_CLASSES)
def test_info_importable(base_class):
    info_cls = Masked(base_class).info.__class__
    assert getattr(core, f"Masked{base_class.__name__}Info") is info_cls


@pytest.mark.parametrize(
    "data",
    [
        Quantity([1, 2, 3], u.m),
        Angle([1, 2, 3], u.deg),
        Latitude([1, 2, 3], u.deg),
        Longitude([1, 2, 3], u.deg),
    ],
)
def test_pickle_masked_with_info(data):
    """Regression test for pickling Masked subclasses with initialized info."""
    mq = Masked(data, mask=[True, False, False])
    mq.info  # Access to trigger dynamic info class creation
    result = pickle.loads(pickle.dumps(mq))
    assert type(result) is type(mq)
    assert all(result.mask == mq.mask)

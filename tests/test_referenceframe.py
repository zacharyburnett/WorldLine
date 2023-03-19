from datetime import timedelta

import pytest

from worldline.model import SpatioTemporal
from worldline.specialrelativity import RelativisticReferenceFrame


@pytest.fixture
def object_1() -> SpatioTemporal:
    object_1 = SpatioTemporal(0, 1)
    object_1.add_velocity_change(10, -1)
    object_1.add_velocity_change(10, 2)
    object_1.add_velocity_change(5, 0)
    object_1.add_velocity_change(20, -1)
    return object_1


@pytest.fixture
def object_2() -> SpatioTemporal:
    object_2 = SpatioTemporal(1, (1, 3, 0))
    object_2.add_velocity_change(10, (-1, 0, -4))
    object_2.add_velocity_change(-10, (-5, -5, -5))
    return object_2


def test_position(object_1, object_2):
    assert tuple(object_1.location_at_time(0)) == (0, 0, 0)
    assert tuple(object_1.location_at_time(15)) == (15, 0, 0)
    assert tuple(object_1.location_at_time(17)) == (19, 0, 0)
    assert tuple(object_1.location_at_time(timedelta(seconds=7))) == (5, 0, 0)
    assert tuple(object_1.location_at_time(20)) == (25, 0, 0)
    assert tuple(object_1.location_at_time(21)) == (24, 0, 0)
    assert tuple(object_1.location_at_time(30)) == (15, 0, 0)
    assert tuple(object_1.location_at_time(timedelta(minutes=0.5))) == (15, 0, 0)
    assert tuple(object_1.location_at_time(timedelta(minutes=1, seconds=1))) == (
        -16,
        0,
        0,
    )

    assert tuple(object_2.location_at_time(0)) == (1, 0, 0)
    assert tuple(object_2.location_at_time(5)) == (6, 15, 0)
    assert tuple(object_2.location_at_time(45)) == (-24, 30, -140)
    assert tuple(object_2.location_at_time(timedelta(minutes=2))) == (-99, 30, -440)
    assert tuple(object_2.location_at_time(-1)) == (0, -3, 0)
    assert tuple(object_2.location_at_time(-5)) == (-4, -15, 0)
    assert tuple(object_2.location_at_time(-11)) == (-60, -83, -50)


def test_velocity(object_1, object_2):
    assert tuple(object_1.velocity(0)) == (1, 0, 0)
    assert tuple(object_1.velocity(15)) == (2, 0, 0)
    assert tuple(object_1.velocity(17)) == (2, 0, 0)
    assert tuple(object_1.velocity(timedelta(seconds=7))) == (0, 0, 0)
    assert tuple(object_1.velocity(20)) == (-1, 0, 0)
    assert tuple(object_1.velocity(21)) == (-1, 0, 0)

    assert tuple(object_2.velocity(0)) == (1, 3, 0)
    assert tuple(object_2.velocity(5)) == (1, 3, 0)
    assert tuple(object_2.velocity(45)) == (-1, 0, -4)
    assert tuple(object_2.velocity(-1)) == (1, 3, 0)
    assert tuple(object_2.velocity(-5)) == (1, 3, 0)
    assert tuple(object_2.velocity(-11)) == (-5, -5, -5)


def test_referenceframe(object_1, object_2):
    reference_frame = RelativisticReferenceFrame()

    reference_frame.add_object(object_1)
    reference_frame.add_object(object_2)

    assert True

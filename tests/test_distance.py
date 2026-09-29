import pytest

from mapy_distance.distance import haversine_km, kilometers_to_miles
from mapy_distance.models import Coordinates


def test_prague_to_vienna_distance() -> None:
    prague = Coordinates(lon=14.4378, lat=50.0755)
    vienna = Coordinates(lon=16.3738, lat=48.2082)

    distance = haversine_km(prague, vienna)

    assert distance == pytest.approx(251.0, abs=1.0)
    assert kilometers_to_miles(distance) == pytest.approx(156.0, abs=1.0)


def test_same_point_has_zero_distance() -> None:
    point = Coordinates(lon=0, lat=0)
    assert haversine_km(point, point) == 0

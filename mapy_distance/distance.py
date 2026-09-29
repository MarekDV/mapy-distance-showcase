"""Straight-line distance calculations for geographic coordinates."""

from math import asin, cos, radians, sin, sqrt

from .models import Coordinates


EARTH_RADIUS_KM = 6371.0088
KM_TO_MILES = 0.621371


def haversine_km(start: Coordinates, end: Coordinates) -> float:
    """Return great-circle distance over a spherical Earth in kilometers.

    Latitude and longitude are angular values, so treating them as ordinary
    Cartesian x/y coordinates would give incorrect results. Haversine converts
    the angles to a central angle before applying the Earth's mean radius.
    """

    lat1, lat2 = radians(start.lat), radians(end.lat)
    delta_lat = radians(end.lat - start.lat)
    delta_lon = radians(end.lon - start.lon)

    haversine = (
        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    )
    central_angle = 2 * asin(sqrt(min(1.0, haversine)))
    return EARTH_RADIUS_KM * central_angle


def kilometers_to_miles(kilometers: float) -> float:
    return kilometers * KM_TO_MILES

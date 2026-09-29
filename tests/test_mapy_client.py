import pytest
import requests
import responses

from mapy_distance.errors import GeocodingError
from mapy_distance.mapy_client import GEOCODE_URL, MapyClient


VALID_RESPONSE = {
    "items": [
        {
            "name": "Prague",
            "label": "Capital city",
            "position": {"lon": 14.4378, "lat": 50.0755},
            "type": "regional.municipality",
            "location": "Czechia",
            "regionalStructure": [],
        }
    ]
}


@responses.activate
def test_geocode_parses_response_and_uses_header_authentication() -> None:
    responses.get(GEOCODE_URL, json=VALID_RESPONSE, status=200)
    client = MapyClient("secret-key")

    candidates = client.geocode("Prague")

    assert candidates[0].name == "Prague"
    assert candidates[0].position.lat == 50.0755
    request = responses.calls[0].request
    assert request.headers["X-Mapy-Api-Key"] == "secret-key"
    assert "secret-key" not in request.url


@responses.activate
def test_missing_destination_is_reported() -> None:
    responses.get(GEOCODE_URL, json={"items": []}, status=200)

    with pytest.raises(GeocodingError, match="could not find"):
        MapyClient("key").geocode("Not a real place")


@pytest.mark.parametrize(
    ("status", "message"),
    [(401, "API key"), (403, "denied"), (429, "rate limit"), (500, "HTTP 500")],
)
@responses.activate
def test_api_failures_have_clear_messages(status: int, message: str) -> None:
    responses.get(GEOCODE_URL, json={"detail": []}, status=status)

    with pytest.raises(GeocodingError, match=message):
        MapyClient("key").geocode("Prague")


def test_network_failure_is_wrapped() -> None:
    session = requests.Session()

    def fail(*args: object, **kwargs: object) -> None:
        raise requests.ConnectionError

    session.get = fail  # type: ignore[method-assign]

    with pytest.raises(GeocodingError, match="connect"):
        MapyClient("key", session=session).geocode("Prague")

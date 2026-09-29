"""Mapy.com forward-geocoding REST client."""

from typing import Any

import requests
from pydantic import ValidationError

from .errors import GeocodingError
from .models import PlaceCandidate


GEOCODE_URL = "https://api.mapy.com/v1/geocode"


class MapyClient:
    """Resolve place names to coordinates using Mapy.com."""

    def __init__(
        self,
        api_key: str,
        timeout: float = 15.0,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()
        # Header authentication avoids exposing the key in URLs and logs.
        self.session.headers.update(
            {
                "Accept": "application/json",
                "X-Mapy-Api-Key": api_key,
                "User-Agent": "mapy-distance-showcase/0.1",
            }
        )

    def geocode(self, query: str, limit: int = 5) -> list[PlaceCandidate]:
        try:
            response = self.session.get(
                GEOCODE_URL,
                params={"query": query, "lang": "en", "limit": limit},
                timeout=self.timeout,
            )
        except requests.Timeout as exc:
            raise GeocodingError("Mapy.com request timed out. Try again.") from exc
        except requests.RequestException as exc:
            raise GeocodingError(
                "Could not connect to Mapy.com. Check your network connection."
            ) from exc

        self._raise_for_status(response)

        try:
            payload: Any = response.json()
            items = payload["items"]
            if not isinstance(items, list):
                raise TypeError
            candidates = [PlaceCandidate.model_validate(item) for item in items]
        except (ValueError, KeyError, TypeError, ValidationError) as exc:
            raise GeocodingError("Mapy.com returned an unexpected response.") from exc

        if not candidates:
            raise GeocodingError(f"Mapy.com could not find '{query}'.")
        return candidates

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        if response.status_code == 401:
            raise GeocodingError("Mapy.com rejected the API key.")
        if response.status_code == 403:
            raise GeocodingError(
                "Mapy.com denied this request. Check the API key restrictions."
            )
        if response.status_code == 429:
            raise GeocodingError("Mapy.com rate limit reached. Try again later.")
        if response.status_code == 422:
            raise GeocodingError("Mapy.com rejected the destination query.")
        if response.status_code >= 400:
            raise GeocodingError(
                f"Mapy.com request failed with HTTP {response.status_code}."
            )

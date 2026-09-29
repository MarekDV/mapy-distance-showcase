"""Validated data exchanged between application components."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .errors import ExtractionError


class DestinationPair(BaseModel):
    """Exactly two non-empty destination names extracted by the LLM."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    origin: str = Field(min_length=1, max_length=150)
    destination: str = Field(min_length=1, max_length=150)

    @model_validator(mode="after")
    def destinations_must_differ(self) -> "DestinationPair":
        if self.origin.casefold() == self.destination.casefold():
            raise ValueError("Origin and destination must be different.")
        return self

    @classmethod
    def from_llm_json(cls, content: str) -> "DestinationPair":
        """Convert an LLM response into trusted application data."""
        try:
            return cls.model_validate_json(content)
        except (ValueError, TypeError) as exc:
            raise ExtractionError(
                "The local model did not return exactly two valid destinations."
            ) from exc


class Coordinates(BaseModel):
    """A longitude/latitude position in WGS 84 degrees."""

    model_config = ConfigDict(extra="forbid")

    lon: float = Field(ge=-180, le=180)
    lat: float = Field(ge=-90, le=90)


class PlaceCandidate(BaseModel):
    """One location candidate returned by Mapy.com geocoding."""

    name: str
    label: str
    position: Coordinates
    type: str
    location: str = ""

    @property
    def display_name(self) -> str:
        details = ", ".join(part for part in (self.location, self.label) if part)
        return f"{self.name} ({details})" if details else self.name

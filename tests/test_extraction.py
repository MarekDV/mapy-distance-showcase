import pytest

from mapy_distance.errors import ExtractionError
from mapy_distance.models import DestinationPair


def test_valid_llm_response() -> None:
    pair = DestinationPair.from_llm_json(
        '{"origin": "Prague", "destination": "Vienna"}'
    )
    assert pair.origin == "Prague"
    assert pair.destination == "Vienna"


@pytest.mark.parametrize(
    "content",
    [
        "Prague and Vienna",
        '{"origin": "Prague"}',
        '{"origin": "", "destination": "Vienna"}',
        '{"origin": "Prague", "destination": "Prague"}',
        '{"origin": "Prague", "destination": "Vienna", "answer": "251 km"}',
    ],
)
def test_invalid_llm_response_is_rejected(content: str) -> None:
    with pytest.raises(ExtractionError):
        DestinationPair.from_llm_json(content)

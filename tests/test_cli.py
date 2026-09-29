from collections.abc import Iterator

from main import choose_candidate, process_sentence, run_cli
from mapy_distance.errors import ExtractionError
from mapy_distance.models import Coordinates, DestinationPair, PlaceCandidate


def place(name: str, lon: float, lat: float, location: str) -> PlaceCandidate:
    return PlaceCandidate(
        name=name,
        label="City",
        position=Coordinates(lon=lon, lat=lat),
        type="regional.municipality",
        location=location,
    )


class FakeExtractor:
    def extract(self, sentence: str) -> DestinationPair:
        if sentence == "bad input":
            raise ExtractionError("Need exactly two destinations.")
        return DestinationPair(origin="Prague", destination="Vienna")


class FakeMapy:
    def geocode(self, query: str) -> list[PlaceCandidate]:
        if query == "Prague":
            return [place("Prague", 14.4378, 50.0755, "Czechia")]
        return [place("Vienna", 16.3738, 48.2082, "Austria")]


def input_sequence(*answers: str):
    values: Iterator[str] = iter(answers)
    return lambda _prompt: next(values)


def test_ambiguous_place_prompts_for_selection() -> None:
    candidates = [
        place("Springfield", -89.65, 39.78, "Illinois, USA"),
        place("Springfield", -93.29, 37.21, "Missouri, USA"),
    ]
    output: list[str] = []

    selected = choose_candidate(
        "Springfield", candidates, input_sequence("wrong", "2"), output.append
    )

    assert selected == candidates[1]
    assert any("Please enter" in line for line in output)


def test_process_sentence_prints_coordinates_method_and_distance() -> None:
    output: list[str] = []

    process_sentence(
        "How far is Prague from Vienna?",
        FakeExtractor(),  # type: ignore[arg-type]
        FakeMapy(),  # type: ignore[arg-type]
        output_fn=output.append,
    )

    text = "\n".join(output)
    assert "Extracted origin: Prague" in text
    assert "50.075500, 14.437800" in text
    assert "Haversine great-circle distance" in text
    assert "Powered by Mapy.com" in text


def test_cli_recovers_from_bad_input_and_quits() -> None:
    output: list[str] = []

    run_cli(
        FakeExtractor(),  # type: ignore[arg-type]
        FakeMapy(),  # type: ignore[arg-type]
        input_sequence("bad input", "q"),
        output.append,
    )

    text = "\n".join(output)
    assert "Error: Need exactly two destinations." in text
    assert text.endswith("Goodbye.")

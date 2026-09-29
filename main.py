"""Command-line entry point for the Mapy.com distance demonstration."""

from collections.abc import Callable

from mapy_distance.config import Settings
from mapy_distance.distance import haversine_km, kilometers_to_miles
from mapy_distance.errors import AppError
from mapy_distance.llm_extractor import DestinationExtractor
from mapy_distance.mapy_client import MapyClient
from mapy_distance.models import PlaceCandidate


InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]
QUIT_COMMANDS = {"q", "quit", "exit"}


def choose_candidate(
    query: str,
    candidates: list[PlaceCandidate],
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> PlaceCandidate | None:
    """Let the user resolve ambiguous geocoding results."""
    if len(candidates) == 1:
        return candidates[0]

    output_fn(f"\nMapy.com found several matches for '{query}':")
    for index, candidate in enumerate(candidates, start=1):
        output_fn(f"  {index}. {candidate.display_name}")

    while True:
        answer = input_fn(
            f"Choose 1-{len(candidates)}, or q to cancel this request: "
        ).strip()
        if answer.casefold() in QUIT_COMMANDS:
            return None
        try:
            selected = int(answer)
            if 1 <= selected <= len(candidates):
                return candidates[selected - 1]
        except ValueError:
            pass
        output_fn("Please enter one of the displayed numbers.")


def process_sentence(
    sentence: str,
    extractor: DestinationExtractor,
    mapy: MapyClient,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> None:
    pair = extractor.extract(sentence)
    output_fn(f"\nExtracted origin: {pair.origin}")
    output_fn(f"Extracted destination: {pair.destination}")

    origin = choose_candidate(
        pair.origin, mapy.geocode(pair.origin), input_fn, output_fn
    )
    if origin is None:
        output_fn("Request cancelled.")
        return

    destination = choose_candidate(
        pair.destination, mapy.geocode(pair.destination), input_fn, output_fn
    )
    if destination is None:
        output_fn("Request cancelled.")
        return

    kilometers = haversine_km(origin.position, destination.position)
    output_fn(f"\nResolved origin: {origin.display_name}")
    output_fn(
        f"  Coordinates: {origin.position.lat:.6f}, {origin.position.lon:.6f}"
    )
    output_fn(f"Resolved destination: {destination.display_name}")
    output_fn(
        f"  Coordinates: {destination.position.lat:.6f}, "
        f"{destination.position.lon:.6f}"
    )
    output_fn("Method: Haversine great-circle distance (calculated locally)")
    output_fn(
        f"Distance: {kilometers:.2f} km "
        f"({kilometers_to_miles(kilometers):.2f} miles)"
    )
    output_fn("Powered by Mapy.com: https://mapy.com/")
    output_fn("Copyright: Seznam.cz a.s. and others — https://api.mapy.com/copyright")


def run_cli(
    extractor: DestinationExtractor,
    mapy: MapyClient,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> None:
    output_fn("Mapy.com Straight-Line Distance Demo")
    output_fn("Enter a sentence with exactly two destinations, or q to quit.")

    while True:
        sentence = input_fn("\nSentence: ").strip()
        if sentence.casefold() in QUIT_COMMANDS:
            output_fn("Goodbye.")
            return
        try:
            process_sentence(sentence, extractor, mapy, input_fn, output_fn)
        except AppError as exc:
            output_fn(f"Error: {exc}")


def main() -> int:
    try:
        settings = Settings.from_environment()
        extractor = DestinationExtractor(settings.ollama_model, settings.ollama_host)
        mapy = MapyClient(settings.mapy_api_key, settings.request_timeout)
        run_cli(extractor, mapy)
        return 0
    except AppError as exc:
        print(f"Error: {exc}")
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

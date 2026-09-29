# Mapy.com Straight-Line Distance Demo

A small Python command-line application demonstrating REST API communication.
It extracts two destinations from a natural-language sentence with a local LLM,
resolves them through Mapy.com, and calculates their great-circle distance.

[![Mapy.com](https://api.mapy.com/img/api/logo.svg)](https://mapy.com/)

Data provided by Mapy.com. Copyright
[Seznam.cz a.s. and others](https://api.mapy.com/copyright).

## Request flow

1. The CLI accepts one sentence.
2. the local `gemma3:1b` model extracts `origin` and `destination`.
3. Pydantic validates the model's structured JSON.
4. Mapy.com's geocoding REST endpoint resolves each name.
5. The user chooses a result when a place name is ambiguous.
6. The Haversine formula calculates the straight-line surface distance.
7. The CLI prints the selected places, coordinates, method, and result.

Each extraction is independent: no conversation history is retained or sent to
the model. Destination extraction remains local; only the extracted place names
are sent to Mapy.com.

## Why the distance is calculated locally

Mapy.com's routing API reports distances along roads, walking paths, or cycling
routes. Those values are not equivalent to flight/straight-line distance. This
application therefore uses Mapy.com for coordinates and calculates the
great-circle distance locally with the Haversine formula and a mean Earth radius
of 6,371.0088 km. It does not treat longitude and latitude as Cartesian values.

## Prerequisites

- Python 3.11 or newer
- [Ollama](https://ollama.com/download)
- A [Mapy.com API project and key](https://developer.mapy.com/my-account/project-and-api-keys/)

The default model is Gemma 3 1B, chosen for low memory usage. Ollama or the model
can still require several gigabytes of free memory while running.

## Installation

In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull gemma3:1b
Copy-Item .env.example .env
```

Edit `.env` and replace the placeholder:

```dotenv
MAPY_API_KEY=your_real_key_here
```

Start Ollama if it is not already running, then run:

```powershell
python main.py
```

## Example

```text
Sentence: How far is Prague from Vienna?

Extracted origin: Prague
Extracted destination: Vienna

Resolved origin: Prague (Czechia, Capital city)
  Coordinates: 50.075500, 14.437800
Resolved destination: Vienna (Austria, Capital city)
  Coordinates: 48.208200, 16.373800
Method: Haversine great-circle distance (calculated locally)
Distance: 251.00 km (155.97 miles)
```

Actual labels and coordinates depend on the current Mapy.com results. Enter
`q`, `quit`, or `exit` at the main prompt to stop.

## Configuration

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `MAPY_API_KEY` | Yes | — | Mapy.com authentication |
| `OLLAMA_MODEL` | No | `gemma3:1b` | Local extraction model |
| `OLLAMA_HOST` | No | `http://localhost:11434` | Local Ollama server |
| `REQUEST_TIMEOUT` | No | `15` | Mapy.com timeout in seconds |

The Mapy.com key is sent in the `X-Mapy-Api-Key` header rather than in the URL.
Never commit `.env`; it is intentionally ignored by Git.

## Tests

```powershell
python -m pytest
```

Tests mock external services and therefore require neither a live API key nor a
running Ollama instance. They cover structured extraction validation, malformed
model output, known Haversine values, geocoding response parsing, authentication
and network failures, ambiguous result selection, and CLI recovery.

## Project structure

```text
main.py                         CLI loop and orchestration
mapy_distance/
  config.py                     Environment settings
  distance.py                   Haversine calculation
  errors.py                     User-facing application errors
  llm_extractor.py              Stateless Ollama extraction
  mapy_client.py                Mapy.com REST client
  models.py                     Pydantic validation models
tests/                          Offline automated tests
.env.example                    Safe configuration template
```

## Error handling

The application reports actionable messages for missing configuration, an
unavailable Ollama server or model, invalid model output, unknown destinations,
Mapy.com authentication failures, rate limits, unexpected responses, and
network timeouts. Normal user errors do not print Python tracebacks.

## Known limitations

- A small model can misunderstand unusually phrased or multilingual input.
- Geocoding ambiguity requires manual selection and can still resolve to an
  unintended place if the sentence lacks a country or region.
- Haversine assumes a spherical Earth; this is appropriate for a demonstration
  but is not a survey-grade ellipsoidal calculation.
- This tool reports straight-line distance, not driving or walking distance.
- Mapy.com requires visible attribution. This README displays the official logo;
  the text-only CLI prints attribution links near each result. Confirm the
  provider's requirements before distributing a terminal-only application.

## API documentation and attribution

- [Mapy.com geocoding overview](https://developer.mapy.com/rest-api-mapy-cz/function/geocoding/)
- [Geocoding OpenAPI specification](https://api.mapy.com/v1/docs/geocode/openapi.json)
- [Mapy.com pricing and credits](https://developer.mapy.com/pricing/)
- [Mapy.com attribution rules](https://developer.mapy.com/rest-api-mapy-cz/atribution/)

Mapy.com's documented geocoding limit is 100 requests per second per API key.
Each successful user request normally performs two geocoding calls.

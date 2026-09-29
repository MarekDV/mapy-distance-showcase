"""Extract destination names with a small, stateless local LLM."""

from ollama import Client

from .errors import ExtractionError
from .models import DestinationPair


SYSTEM_PROMPT = """You extract geographic destinations from one user sentence.
Return only data matching the supplied JSON schema.
Set origin to the place being travelled from and destination to the place being
travelled to. Preserve useful qualifiers such as country or state. Do not answer
the distance question. If the sentence does not contain exactly two geographic
destinations, use empty strings for fields you cannot identify."""


class DestinationExtractor:
    """Thin wrapper around Ollama's local chat API."""

    def __init__(self, model: str, host: str) -> None:
        self.model = model
        self.client = Client(host=host)

    def extract(self, sentence: str) -> DestinationPair:
        sentence = sentence.strip()
        if not sentence:
            raise ExtractionError("Enter a sentence containing two destinations.")

        try:
            # A fresh message list on every call prevents conversation history.
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": sentence},
                ],
                format=DestinationPair.model_json_schema(),
                stream=False,
                options={"temperature": 0, "num_ctx": 2048},
            )
            content = response.message.content
        except Exception as exc:
            raise ExtractionError(
                f"Could not use Ollama model '{self.model}'. "
                f"Ensure Ollama is running and run: ollama pull {self.model}"
            ) from exc

        return DestinationPair.from_llm_json(content)

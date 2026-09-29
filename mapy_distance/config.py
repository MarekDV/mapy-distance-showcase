"""Environment-based application configuration."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .errors import ConfigurationError


@dataclass(frozen=True)
class Settings:
    mapy_api_key: str
    ollama_model: str = "gemma3:1b"
    ollama_host: str = "http://localhost:11434"
    request_timeout: float = 15.0

    @classmethod
    def from_environment(cls) -> "Settings":
        """Load local settings without placing secrets in source code."""
        load_dotenv()
        api_key = os.getenv("MAPY_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "MAPY_API_KEY is missing. Copy .env.example to .env and add your key."
            )

        try:
            timeout = float(os.getenv("REQUEST_TIMEOUT", "15"))
            if timeout <= 0:
                raise ValueError
        except ValueError as exc:
            raise ConfigurationError("REQUEST_TIMEOUT must be a positive number.") from exc

        return cls(
            mapy_api_key=api_key,
            ollama_model=os.getenv("OLLAMA_MODEL", "gemma3:1b").strip()
            or "gemma3:1b",
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/"),
            request_timeout=timeout,
        )

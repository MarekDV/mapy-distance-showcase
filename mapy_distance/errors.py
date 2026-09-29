"""Application-specific exceptions with user-friendly messages."""


class AppError(Exception):
    """Base exception for errors that can be shown without a traceback."""


class ConfigurationError(AppError):
    """Raised when required configuration is absent or invalid."""


class ExtractionError(AppError):
    """Raised when destinations cannot be extracted or validated."""


class GeocodingError(AppError):
    """Raised when Mapy.com cannot resolve a destination."""

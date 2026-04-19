"""Custom exceptions for uncertainAPI."""

class UncertainAPIError(Exception):
    """Base exception for uncertainAPI."""

class ExtractorError(UncertainAPIError):
    """Base exception for extraction operations."""

class AuthenticationError(ExtractorError):
    """Raised when authentication fails."""

class CaptchaError(ExtractorError):
    """Raised when captcha handling fails."""

class ExtractionError(ExtractorError):
    """Raised when data extraction fails."""

class BrowserError(ExtractorError):
    """Raised when browser operations fail."""

class ConfigurationError(UncertainAPIError):
    """Raised when configuration is invalid."""

class ProviderError(UncertainAPIError):
    """Raised when AI provider operations fail."""




"""OpenAI integration exceptions."""


class OpenAIError(Exception):
    """Base exception for OpenAI integration errors."""


class OpenAIConfigurationError(OpenAIError):
    """Exception raised when OpenAI configuration is invalid."""


class OpenAIAPIError(OpenAIError):
    """Exception raised when OpenAI API call fails."""

"""Converters."""


class ConverterBase:
    """Base class for converters."""

    def to_python(self, value: str) -> str:  # pylint:disable=no-self-use
        """To python."""
        return value

    def to_url(self, value: str) -> str:  # pylint:disable=no-self-use
        """To URL."""
        return value


class ListConverter(ConverterBase):
    """List converter."""

    regex = "watched|to-watch"


class FeedConverter(ConverterBase):
    """Feed converter."""

    regex = "people|friends"

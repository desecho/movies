class Converter:
    def to_python(self, value: str) -> str:  # pylint:disable=no-self-use
        return value

    def to_url(self, value: str) -> str:  # pylint:disable=no-self-use
        return value


class ListConverter(Converter):
    regex = "watched|to-watch"


class FeedConverter(Converter):
    regex = "people|friends"

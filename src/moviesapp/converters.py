class Converter:
    def to_python(self, value):
        return value

    def to_url(self, value):
        return value

class ListConverter(Converter):
    regex = "watched|to-watch"

class FeedConverter(Converter):
    regex = "people|friends"

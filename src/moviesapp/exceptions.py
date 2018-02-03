class MovieNotInDb(Exception):
    """
    Movie is not in DB.

    It means the movie does not have an IMDB id.
    """

    pass


class NotAvailableSearchType(Exception):
    """Not availabe search type."""

    pass

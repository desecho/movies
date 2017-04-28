class MovieNotInDb(Exception):
    """It means the movie does not have an IMDB id."""
    pass


class NotAvailableSearchType(Exception):
    pass

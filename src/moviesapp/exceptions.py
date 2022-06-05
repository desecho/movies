class MovieNotInDb(Exception):
    """
    Movie is not in DB.

    It means the movie does not have an IMDB id.
    """


class NotAvailableSearchType(Exception):
    """Not availabe search type."""


class OmdbLimitReached(Exception):
    """OMDb limit reached."""


class OmdbRequestError(Exception):
    """OMDb request error."""


class OmdbError(Exception):
    """OMDb error."""


class VKError(Exception):
    """VK error."""


class TrailerSiteNotFoundError(Exception):
    """Trailer site not found error."""

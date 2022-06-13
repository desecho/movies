"""OMDb exceptions."""


class OmdbLimitReachedError(Exception):
    """OMDb limit reached."""


class OmdbRequestError(Exception):
    """OMDb request error."""


class OmdbError(Exception):
    """OMDb error."""

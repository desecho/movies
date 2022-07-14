"""OMDb types."""
from __future__ import annotations

from typing import Literal, Optional

from typing_extensions import NotRequired, TypedDict

from ..types import UntypedObject

# OMDB does not provide types. We assume these types by experimentation.


class OmdbMovie(TypedDict):
    """OMDb movie."""

    Title: str
    Year: str
    Rated: str
    Released: str
    Runtime: str
    Genre: str
    Director: str
    Writer: str
    Actors: str
    Plot: str
    Language: str
    Country: str
    Awards: str
    Poster: str
    Ratings: list[UntypedObject]  # We can set better type for this but it is not used so that is not necessary.
    Metascore: str
    imdbRating: str
    imdbVotes: str
    imdbID: str
    Type: str
    DVD: str
    BoxOffice: str
    Production: str
    Website: str
    Response: str
    Error: NotRequired[str]


class OmdbMoviePreprocessed(TypedDict):
    """OMDb movie preprocessed."""

    Writer: Optional[str]
    Director: Optional[str]
    Actors: Optional[str]
    Genre: Optional[str]
    Country: Optional[str]
    imdbRating: Optional[str]


OmdbMoviePreprocessedKey = Literal["Writer", "Actors", "Director", "Genre", "Country", "imdbRating"]

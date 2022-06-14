"""OMDb types."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional, TypeAlias

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
    Ratings: List[UntypedObject]  # We can set better type for this but it is not used so that is not necessary.
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


class OmdbMovieProcessed(TypedDict):
    """OMDb movie processed."""

    writer: Optional[str]
    director: Optional[str]
    actors: Optional[str]
    genre: Optional[str]
    country: Optional[str]
    imdb_rating: Optional[str]
    runtime: OmdbRuntime


class OmdbMoviePreprocessed(TypedDict):
    """OMDb movie preprocessed."""

    Writer: Optional[str]
    Director: Optional[str]
    Actors: Optional[str]
    Genre: Optional[str]
    Country: Optional[str]
    imdbRating: Optional[str]
    Runtime: Optional[str]


OmdbRuntime: TypeAlias = Optional[datetime]
OmdbMoviePreprocessedKey = Literal["Writer", "Actors", "Director", "Genre", "Country", "imdbRating", "Runtime"]

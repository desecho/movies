"""OpenAI integration type definitions."""

from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict

from django.conf import settings


@dataclass
class RecommendationRequest:
    """Request structure for movie recommendations."""

    liked_movies: Optional[List[str]] = None
    disliked_movies: Optional[List[str]] = None
    preferred_genre: Optional[str] = None
    year_range: Optional[Dict[str, int]] = None  # {"start": 2000, "end": 2023}
    min_rating: Optional[int] = None  # Rating on a 5-star scale
    recommendations_number: Optional[int] = settings.AI_MAX_RECOMMENDATIONS


@dataclass
class MovieRecommendation:
    """Single movie recommendation."""

    title: str
    description: str
    confidence_score: Optional[float] = None


@dataclass
class IMDbItem(TypedDict):
    imdb_id: str


RecommendationResponse = List[IMDbItem]

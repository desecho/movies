"""Stats views."""

from datetime import datetime, timedelta
from typing import Any, Dict, List as ListType, cast

from django.db.models import Avg, Count
from django.db.models.query import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import List, Record, User


class StatsView(APIView):
    """Stats view."""

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Get user statistics."""
        user: User = cast(User, request.user)

        # Get all user records
        user_records = user.get_records()
        watched_records = user_records.filter(list_id=List.WATCHED)
        to_watch_records = user_records.filter(list_id=List.TO_WATCH)

        # Calculate basic stats
        basic_stats = self._get_basic_stats(watched_records, to_watch_records)

        # Calculate time and rating stats
        time_rating_stats = self._get_time_and_rating_stats(watched_records)

        # Get preference stats
        preference_stats = self._get_preference_stats(watched_records)

        # Get trend stats
        trend_stats = self._get_trend_stats(watched_records)

        # Combine all stats
        stats = {
            **basic_stats,
            **time_rating_stats,
            **preference_stats,
            **trend_stats,
        }

        return Response(stats)

    @staticmethod
    def _get_basic_stats(watched_records: "QuerySet[Record]", to_watch_records: "QuerySet[Record]") -> Dict[str, int]:
        """Get basic count statistics."""
        return {
            "totalMoviesWatched": watched_records.count(),
            "totalMoviesToWatch": to_watch_records.count(),
        }

    @staticmethod
    def _get_time_and_rating_stats(watched_records: "QuerySet[Record]") -> Dict[str, Any]:
        """Get time watched and rating statistics."""
        # Calculate total hours watched
        total_hours = 0.0
        for record in watched_records.select_related("movie"):
            if record.movie.runtime:
                runtime_seconds = (
                    record.movie.runtime.hour * 3600 + record.movie.runtime.minute * 60 + record.movie.runtime.second
                )
                total_hours += runtime_seconds / 3600

        # Rating statistics
        rated_movies = watched_records.filter(rating__gt=0)
        rating_stats = rated_movies.aggregate(average_rating=Avg("rating"), total_rated=Count("rating"))

        return {
            "totalHoursWatched": round(total_hours, 1),
            "averageRating": round(rating_stats["average_rating"], 1) if rating_stats["average_rating"] else None,
            "totalRatedMovies": rating_stats["total_rated"],
        }

    def _get_preference_stats(self, watched_records: "QuerySet[Record]") -> Dict[str, Any]:
        """Get quality preferences and top genres/directors."""
        # Quality preferences
        quality_stats = {
            "theatre": watched_records.filter(watched_in_theatre=True).count(),
            "hd": watched_records.filter(watched_in_hd=True).count(),
            "fullHd": watched_records.filter(watched_in_full_hd=True).count(),
            "fourK": watched_records.filter(watched_in_4k=True).count(),
            "extended": watched_records.filter(watched_extended=True).count(),
            "original": watched_records.filter(watched_original=True).count(),
        }

        # Top genres, directors, and actors
        genre_counts = self._count_comma_separated_field(watched_records, "genre")
        director_counts = self._count_comma_separated_field(watched_records, "director")
        actor_counts = self._count_comma_separated_field(watched_records, "actors")

        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_directors = sorted(director_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_actors = sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "qualityPreferences": quality_stats,
            "topGenres": [{"name": name, "count": count} for name, count in top_genres],
            "topDirectors": [{"name": name, "count": count} for name, count in top_directors],
            "topActors": [{"name": name, "count": count} for name, count in top_actors],
        }

    @staticmethod
    def _get_trend_stats(watched_records: "QuerySet[Record]") -> Dict[str, Any]:
        """Get monthly trends and rating distribution."""
        # Monthly watching trends (last 12 months)
        monthly_stats: ListType[Dict[str, Any]] = []
        current_date = datetime.now()
        for i in range(12):
            month_start = current_date.replace(day=1) - timedelta(days=30 * i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            month_count = watched_records.filter(date__gte=month_start, date__lte=month_end).count()
            monthly_stats.append({"month": month_start.strftime("%Y-%m"), "count": month_count})
        monthly_stats.reverse()

        # Rating distribution
        rating_distribution: Dict[str, int] = {}
        for i in range(1, 11):
            count = watched_records.filter(rating=i).count()
            if count > 0:
                rating_distribution[str(i)] = count

        return {
            "monthlyTrends": monthly_stats,
            "ratingDistribution": rating_distribution,
        }

    @staticmethod
    def _count_comma_separated_field(records: "QuerySet[Record]", field_name: str) -> Dict[str, int]:
        """Count occurrences in comma-separated field."""
        counts: Dict[str, int] = {}
        for record in records.select_related("movie"):
            field_value = getattr(record.movie, field_name, None)
            if field_value:
                items = [item.strip() for item in field_value.split(",")]
                for item in items:
                    if item:
                        counts[item] = counts.get(item, 0) + 1
        return counts

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

        # Get year parameter from query string
        year = request.query_params.get("year")

        # Get all user records
        user_records = user.get_records()
        watched_records = user_records.filter(list_id=List.WATCHED)
        to_watch_records = user_records.filter(list_id=List.TO_WATCH)

        # Filter by year if specified
        if year:
            try:
                year_int = int(year)
                watched_records = watched_records.filter(date__year=year_int)
                to_watch_records = to_watch_records.filter(date__year=year_int)
            except ValueError:
                pass  # Invalid year, use all records

        # Calculate basic stats
        basic_stats = self._get_basic_stats(watched_records, to_watch_records)

        # Calculate time and rating stats
        time_rating_stats = self._get_time_and_rating_stats(watched_records)

        # Get preference stats
        preference_stats = self._get_preference_stats(watched_records)

        # Get trend stats
        trend_stats = self._get_trend_stats(watched_records)

        # Get release date stats
        release_date_stats = self._get_release_date_stats(watched_records)

        # Always get available years for the selector
        available_years = self._get_available_years(user)

        # Get yearly stats if year is specified
        yearly_stats = {}
        if year:
            yearly_stats = self._get_yearly_stats(user, year_int)
        else:
            # Include available years even when no year is selected
            yearly_stats = {"availableYears": available_years}

        # Combine all stats
        stats = {
            **basic_stats,
            **time_rating_stats,
            **preference_stats,
            **trend_stats,
            **release_date_stats,
            **yearly_stats,
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

    def _get_yearly_stats(self, user: User, year: int) -> Dict[str, Any]:
        """Get yearly statistics and year-in-review data."""
        if not year:
            return {}

        current_year = datetime.now().year

        # Get records for the specified year
        yearly_records = user.get_records().filter(list_id=List.WATCHED, date__year=year)

        # Get records for previous year for comparison
        previous_year_records = user.get_records().filter(list_id=List.WATCHED, date__year=year - 1)

        # Basic yearly overview
        yearly_overview = self._get_yearly_overview(yearly_records, previous_year_records)

        # Yearly milestones
        yearly_milestones = self._get_yearly_milestones(yearly_records)

        # Available years for selector
        available_years = self._get_available_years(user)

        return {
            "yearlyOverview": yearly_overview,
            "yearlyMilestones": yearly_milestones,
            "availableYears": available_years,
            "selectedYear": year,
            "isCurrentYear": year == current_year,
        }

    @staticmethod
    def _get_yearly_overview(
        yearly_records: "QuerySet[Record]", previous_year_records: "QuerySet[Record]"
    ) -> Dict[str, Any]:
        """Get yearly overview with comparisons."""
        current_count = yearly_records.count()
        previous_count = previous_year_records.count()

        # Calculate year-over-year change
        year_change = current_count - previous_count
        year_change_percent = (year_change / previous_count * 100) if previous_count > 0 else 0

        # Calculate total hours for the year
        total_hours = 0.0
        for record in yearly_records.select_related("movie"):
            if record.movie.runtime:
                runtime_seconds = (
                    record.movie.runtime.hour * 3600 + record.movie.runtime.minute * 60 + record.movie.runtime.second
                )
                total_hours += runtime_seconds / 3600

        # Monthly distribution for the year
        monthly_distribution = []
        for month in range(1, 13):
            month_count = yearly_records.filter(date__month=month).count()
            monthly_distribution.append({"month": month, "count": month_count})

        # Find peak month
        peak_month = (
            max(monthly_distribution, key=lambda x: x["count"]) if monthly_distribution else {"month": 1, "count": 0}
        )

        return {
            "totalMoviesWatched": current_count,
            "totalHoursWatched": round(total_hours, 1),
            "yearOverYearChange": year_change,
            "yearOverYearChangePercent": round(year_change_percent, 1),
            "peakMonth": peak_month["month"],
            "peakMonthCount": peak_month["count"],
            "monthlyDistribution": monthly_distribution,
        }

    def _get_yearly_milestones(self, yearly_records: "QuerySet[Record]") -> Dict[str, Any]:
        """Get yearly milestones and achievements."""
        if not yearly_records.exists():
            return {}

        # First and last movie of the year
        first_movie = yearly_records.order_by("date").first()
        last_movie = yearly_records.order_by("-date").first()

        # Highest rated movie
        highest_rated = yearly_records.filter(rating__gt=0).order_by("-rating", "-date").first()

        # Longest movie watched
        longest_movie = None
        max_runtime = 0
        for record in yearly_records.select_related("movie"):
            if record.movie.runtime:
                runtime_seconds = (
                    record.movie.runtime.hour * 3600 + record.movie.runtime.minute * 60 + record.movie.runtime.second
                )
                if runtime_seconds > max_runtime:
                    max_runtime = runtime_seconds
                    longest_movie = record

        # Get top items using helper methods
        top_genre_data = self._get_top_item_from_field(yearly_records, "genre")
        top_director_data = self._get_top_item_from_field(yearly_records, "director")
        top_actor_data = self._get_top_item_from_field(yearly_records, "actors")

        milestones = {
            "firstMovie": (
                {
                    "title": first_movie.movie.title,
                    "date": first_movie.date.strftime("%Y-%m-%d"),
                }
                if first_movie
                else None
            ),
            "lastMovie": (
                {
                    "title": last_movie.movie.title,
                    "date": last_movie.date.strftime("%Y-%m-%d"),
                }
                if last_movie
                else None
            ),
            "highestRatedMovie": (
                {
                    "title": highest_rated.movie.title,
                    "rating": highest_rated.rating,
                    "date": highest_rated.date.strftime("%Y-%m-%d"),
                }
                if highest_rated
                else None
            ),
            "longestMovie": (
                {
                    "title": longest_movie.movie.title,
                    "runtime": longest_movie.movie.runtime_formatted,
                }
                if longest_movie
                else None
            ),
            "topGenre": top_genre_data,
            "topDirector": top_director_data,
            "topActor": top_actor_data,
        }

        return milestones

    @staticmethod
    def _get_top_item_from_field(records: "QuerySet[Record]", field_name: str) -> Dict[str, Any] | None:
        """Get the most frequent item from a comma-separated field."""
        counts: Dict[str, int] = {}
        for record in records.select_related("movie"):
            field_value = getattr(record.movie, field_name, None)
            if field_value:
                items = [item.strip() for item in field_value.split(",")]
                for item in items:
                    if item:
                        counts[item] = counts.get(item, 0) + 1

        if not counts:
            return None

        top_item_tuple = max(counts.items(), key=lambda x: x[1])
        return {
            "name": top_item_tuple[0],
            "count": top_item_tuple[1],
        }

    @staticmethod
    def _get_available_years(user: User) -> ListType[int]:
        """Get list of years with watch activity."""
        years = user.get_records().filter(list_id=List.WATCHED).dates("date", "year")
        year_list = sorted({date.year for date in years}, reverse=True)
        return year_list

    @staticmethod
    def _get_release_date_stats(watched_records: "QuerySet[Record]") -> Dict[str, Any]:
        """Get release date statistics."""
        # Get records with release dates
        records_with_dates = watched_records.select_related("movie").filter(movie__release_date__isnull=False)

        if not records_with_dates.exists():
            return {
                "decadeDistribution": {},
                "averageReleaseYear": None,
                "oldestMovie": None,
                "newestMovie": None,
                "topReleaseYears": [],
                "vintagePreferences": {
                    "classic": 0,  # Pre-1980
                    "retro": 0,  # 1980-1999
                    "modern": 0,  # 2000-2009
                    "recent": 0,  # 2010+
                },
            }

        # Collect release years
        release_years = []
        oldest_record = None
        newest_record = None

        for record in records_with_dates:
            if record.movie.release_date:
                release_year = record.movie.release_date.year
                release_years.append(release_year)

                # Track oldest and newest movies
                if (
                    oldest_record is None
                    or oldest_record.movie.release_date is None
                    or record.movie.release_date < oldest_record.movie.release_date
                ):
                    oldest_record = record
                if (
                    newest_record is None
                    or newest_record.movie.release_date is None
                    or record.movie.release_date > newest_record.movie.release_date
                ):
                    newest_record = record

        # Calculate decade distribution
        decade_counts: Dict[str, int] = {}
        year_counts: Dict[int, int] = {}

        for year in release_years:
            # Decade calculation (e.g., 1985 -> 1980s)
            decade = (year // 10) * 10
            decade_label = f"{decade}s"
            decade_counts[decade_label] = decade_counts.get(decade_label, 0) + 1

            # Year counts for top years
            year_counts[year] = year_counts.get(year, 0) + 1

        # Calculate vintage preferences
        classic_count = sum(1 for year in release_years if year < 1980)
        retro_count = sum(1 for year in release_years if 1980 <= year < 2000)
        modern_count = sum(1 for year in release_years if 2000 <= year < 2010)
        recent_count = sum(1 for year in release_years if year >= 2010)

        # Get top release years (limit to 5)
        top_years = sorted(year_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Calculate average release year
        average_year = sum(release_years) / len(release_years) if release_years else None

        return {
            "decadeDistribution": decade_counts,
            "averageReleaseYear": round(average_year, 1) if average_year else None,
            "oldestMovie": (
                {
                    "title": oldest_record.movie.title,
                    "releaseDate": oldest_record.movie.release_date.strftime("%Y-%m-%d"),
                    "releaseYear": oldest_record.movie.release_date.year,
                }
                if oldest_record and oldest_record.movie.release_date
                else None
            ),
            "newestMovie": (
                {
                    "title": newest_record.movie.title,
                    "releaseDate": newest_record.movie.release_date.strftime("%Y-%m-%d"),
                    "releaseYear": newest_record.movie.release_date.year,
                }
                if newest_record and newest_record.movie.release_date
                else None
            ),
            "topReleaseYears": [{"year": year, "count": count} for year, count in top_years],
            "vintagePreferences": {
                "classic": classic_count,
                "retro": retro_count,
                "modern": modern_count,
                "recent": recent_count,
            },
        }

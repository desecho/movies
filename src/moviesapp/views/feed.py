"""Feed views."""

from typing import TYPE_CHECKING, Any, Union

from django.db.models import Q, QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ActionRecord, Follow

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission


class FeedPagination(PageNumberPagination):
    """Feed pagination."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class FeedView(APIView):
    """Feed view."""

    permission_classes: list[type["BasePermission"]] = []
    pagination_class = FeedPagination

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Return activity feed."""
        user = request.user

        # Base query for all action records with related data
        if user.is_authenticated:
            # Authenticated user - exclude hidden users and only_for_friends unless they're friends
            base_query = (
                ActionRecord.objects.select_related("user", "action", "movie", "list")
                .exclude(Q(user__hidden=True) | (Q(user__only_for_friends=True) & ~Q(user=user)))
                .order_by("-date")
            )
        else:
            # Anonymous user - exclude hidden users and all only_for_friends users
            base_query = (
                ActionRecord.objects.select_related("user", "action", "movie", "list")
                .exclude(Q(user__hidden=True) | Q(user__only_for_friends=True))
                .order_by("-date")
            )

        # Determine which users' activity to show
        if user.is_authenticated:
            # Get users that the current user follows
            following_users = Follow.objects.filter(follower=user).values_list("followed_id", flat=True)

            if following_users.exists():
                # Show only activity from followed users
                queryset = base_query.filter(user_id__in=following_users)
            else:
                # User is not following anyone, show all activity
                queryset = base_query
        else:
            # Anonymous user - show all activity
            queryset = base_query

        # Apply pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            data = self._serialize_actions(page)
            return paginator.get_paginated_response(data)

        data = self._serialize_actions(queryset)
        return Response(data)

    # pylint: disable=no-self-use
    def _serialize_actions(
        self, actions: Union[QuerySet[ActionRecord, ActionRecord], list[ActionRecord]]
    ) -> list[dict[str, Any]]:
        """Serialize action records for the feed."""
        feed_data = []

        for action in actions:
            item = {
                "id": action.id,
                "user": {
                    "username": action.user.username,
                    "avatar_url": action.user.avatar.url if action.user.avatar else None,
                },
                "action": {
                    "id": action.action.id,
                    "name": action.action.name,
                },
                "movie": {
                    "id": action.movie.id,
                    "title": action.movie.title,
                    "poster_small": action.movie.poster_small,
                    "release_date": action.movie.release_date_formatted,
                    "tmdb_id": action.movie.tmdb_id,
                },
                "date": action.date,
            }

            # Add optional fields based on action type
            if action.list:
                item["list"] = {
                    "id": action.list.id,
                    "name": action.list.name,
                }

            if action.rating:
                item["rating"] = action.rating

            if action.comment:
                item["comment"] = action.comment

            feed_data.append(item)

        return feed_data

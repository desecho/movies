"""User follows views."""

from typing import TYPE_CHECKING, cast

from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Follow, User

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission


class UserFollowingView(APIView):
    """View for current user's following list."""

    permission_classes: list[type["BasePermission"]] = [IsAuthenticated]

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Get list of users that current user follows."""
        # Get users that the current user follows
        user = cast(User, request.user)  # Safe because of IsAuthenticated permission
        following_relationships = Follow.objects.filter(follower=user).select_related("followed").order_by("-date")

        following_users = []
        for relationship in following_relationships:
            followed_user = relationship.followed
            # Don't include hidden users in the list
            if not followed_user.hidden:
                following_users.append(
                    {
                        "username": followed_user.username,
                        "avatar_url": followed_user.avatar.url if followed_user.avatar else None,
                        "follow_date": relationship.date,
                    }
                )

        return Response(
            {
                "count": len(following_users),
                "results": following_users,
            }
        )


class UserFollowersView(APIView):
    """View for current user's followers list."""

    permission_classes: list[type["BasePermission"]] = [IsAuthenticated]

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Get list of users that follow current user."""
        # Get users that follow the current user
        user = cast(User, request.user)  # Safe because of IsAuthenticated permission
        follower_relationships = Follow.objects.filter(followed=user).select_related("follower").order_by("-date")

        followers = []
        for relationship in follower_relationships:
            follower_user = relationship.follower
            # Don't include hidden users in the list
            if not follower_user.hidden:
                followers.append(
                    {
                        "username": follower_user.username,
                        "avatar_url": follower_user.avatar.url if follower_user.avatar else None,
                        "follow_date": relationship.date,
                    }
                )

        return Response(
            {
                "count": len(followers),
                "results": followers,
            }
        )


class PublicUserFollowingView(APIView):
    """View for any user's following list (public)."""

    permission_classes: list[type["BasePermission"]] = []

    def get(self, request: Request, username: str) -> Response:  # pylint: disable=no-self-use,unused-argument
        """Get list of users that specified user follows."""
        try:
            target_user = User.objects.get(username=username, hidden=False)
        except User.DoesNotExist as exc:
            raise Http404("User not found") from exc

        # Check if target user allows public viewing of their follows
        # For now, we'll show following list publicly unless user is hidden
        # In the future, you might want to add a privacy setting for this

        # Get users that the target user follows
        following_relationships = (
            Follow.objects.filter(follower=target_user).select_related("followed").order_by("-date")
        )

        following_users = []
        for relationship in following_relationships:
            followed_user = relationship.followed
            # Only include non-hidden users in public view
            if not followed_user.hidden:
                following_users.append(
                    {
                        "username": followed_user.username,
                        "avatar_url": followed_user.avatar.url if followed_user.avatar else None,
                        "follow_date": relationship.date,
                    }
                )

        return Response(
            {
                "user": target_user.username,
                "count": len(following_users),
                "results": following_users,
            }
        )


class PublicUserFollowersView(APIView):
    """View for any user's followers list (public)."""

    permission_classes: list[type["BasePermission"]] = []

    def get(self, request: Request, username: str) -> Response:  # pylint: disable=no-self-use,unused-argument
        """Get list of users that follow specified user."""
        try:
            target_user = User.objects.get(username=username, hidden=False)
        except User.DoesNotExist as exc:
            raise Http404("User not found") from exc

        # Get users that follow the target user
        follower_relationships = (
            Follow.objects.filter(followed=target_user).select_related("follower").order_by("-date")
        )

        followers = []
        for relationship in follower_relationships:
            follower_user = relationship.follower
            # Only include non-hidden users in public view
            if not follower_user.hidden:
                followers.append(
                    {
                        "username": follower_user.username,
                        "avatar_url": follower_user.avatar.url if follower_user.avatar else None,
                        "follow_date": relationship.date,
                    }
                )

        return Response(
            {
                "user": target_user.username,
                "count": len(followers),
                "results": followers,
            }
        )

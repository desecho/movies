"""Follow views."""

from typing import TYPE_CHECKING, List, cast

from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Follow, User

if TYPE_CHECKING:
    pass


class FollowView(APIView):
    """Follow/Unfollow view."""

    def get_permissions(self) -> List[IsAuthenticated]:
        """Return different permissions for different methods."""
        if self.request.method == "GET":
            # Allow unauthenticated access for GET requests
            return []
        # Require authentication for POST and DELETE
        return [IsAuthenticated()]

    def get(self, request: Request, username: str) -> Response:  # pylint: disable=no-self-use
        """Check if current user is following the specified user."""
        try:
            target_user = User.objects.get(username=username, hidden=False)
        except User.DoesNotExist as exc:
            raise Http404("User not found") from exc

        if not request.user.is_authenticated:
            return Response({"is_following": False})

        # Since this view has IsAuthenticated permission, request.user is guaranteed to be a User instance
        is_following = Follow.objects.filter(follower=request.user, followed=target_user).exists()

        # Get follow counts
        followers_count = target_user.followers.count()
        following_count = target_user.following.count()

        return Response(
            {
                "is_following": is_following,
                "followers_count": followers_count,
                "following_count": following_count,
            }
        )

    def post(self, request: Request, username: str) -> Response:  # pylint: disable=no-self-use
        """Follow a user."""
        try:
            target_user = User.objects.get(username=username, hidden=False)
        except User.DoesNotExist as exc:
            raise Http404("User not found") from exc

        # Prevent self-following
        user = cast(User, request.user)  # Safe because of IsAuthenticated permission
        if user == target_user:
            return Response({"error": "Cannot follow yourself"}, status=400)

        # Create follow relationship if it doesn't exist
        _, created = Follow.objects.get_or_create(follower=user, followed=target_user)

        if created:
            message = f"You are now following {target_user.username}"
            status = 201
        else:
            message = f"You are already following {target_user.username}"
            status = 200

        # Get updated counts
        followers_count = target_user.followers.count()
        following_count = target_user.following.count()

        return Response(
            {
                "message": message,
                "is_following": True,
                "followers_count": followers_count,
                "following_count": following_count,
            },
            status=status,
        )

    def delete(self, request: Request, username: str) -> Response:  # pylint: disable=no-self-use
        """Unfollow a user."""
        try:
            target_user = User.objects.get(username=username, hidden=False)
        except User.DoesNotExist as exc:
            raise Http404("User not found") from exc

        # Remove follow relationship
        user = cast(User, request.user)  # Safe because of IsAuthenticated permission
        deleted, _ = Follow.objects.filter(follower=user, followed=target_user).delete()

        if deleted:
            message = f"You have unfollowed {target_user.username}"
        else:
            message = f"You were not following {target_user.username}"

        # Get updated counts
        followers_count = target_user.followers.count()
        following_count = target_user.following.count()

        return Response(
            {
                "message": message,
                "is_following": False,
                "followers_count": followers_count,
                "following_count": following_count,
            }
        )

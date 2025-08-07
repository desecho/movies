"""Set user avatar field to local avatar paths."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from moviesapp.models import User


class Command(BaseCommand):
    """Set user avatar field to local avatar paths command."""

    help = "Set user avatar field to point to local avatar files"

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments."""
        parser.add_argument(
            "--folder",
            default="avatars",
            help="Folder where avatars are stored (default: avatars)",
        )
        parser.add_argument(
            "--extension",
            default="jpg",
            help="Avatar file extension (default: jpg)",
        )
        parser.add_argument(
            "--check-files",
            action="store_true",
            help="Only set avatar if the file actually exists on disk",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle command."""
        folder = options["folder"]
        extension = options["extension"]
        check_files = options["check_files"]

        # Get all users with usernames
        users = User.objects.exclude(username="").exclude(username__isnull=True)

        if not users.exists():
            self.stdout.write(self.style.WARNING("No users found with usernames"))
            return

        self.stdout.write(f"Found {users.count()} users with usernames")

        updated = 0
        skipped = 0
        not_found = 0

        for user in users:
            username = user.username
            avatar_path = f"{folder}/{username}.{extension}"

            # Check if avatar is already set to this path
            if user.avatar:
                self.stdout.write(f"Skipped {username} (already set)")
                skipped += 1
                continue

            # Set the avatar field
            user.avatar.name = avatar_path
            user.save(update_fields=["avatar"])

            self.stdout.write(self.style.SUCCESS(f"Set avatar for {username}: {avatar_path}"))
            updated += 1

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Updated: {updated}")
        self.stdout.write(f"Skipped: {skipped}")
        if check_files:
            self.stdout.write(f"Files not found: {not_found}")
        self.stdout.write(f"Total users processed: {users.count()}")

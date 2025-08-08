"""Serializers."""

from typing import Any

from django.conf import settings
from django_countries import countries
from PIL import Image
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from .models import User


def validate_avatar_image(image: Any) -> Any:
    """Validate avatar image format and dimensions."""
    if not image:
        return image

    # Check file extension
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    file_extension = image.name.lower().split(".")[-1]
    if f".{file_extension}" not in allowed_extensions:
        raise ValidationError("Avatar must be a JPEG or PNG image.")

    # Check image dimensions using Pillow
    try:
        pil_image = Image.open(image)
        width, height = pil_image.size
        max_dimension = settings.AVATAR_MAX_DIMENSION

        if width > max_dimension or height > max_dimension:
            raise ValidationError(f"Avatar dimensions cannot exceed {max_dimension}x{max_dimension} pixels.")

    except Exception as e:
        raise ValidationError("Invalid image file.") from e

    # Reset file pointer
    image.seek(0)
    return image


class AvatarUploadSerializer(serializers.ModelSerializer[User]):
    """Avatar upload serializer."""

    avatar = serializers.ImageField(validators=[validate_avatar_image])

    class Meta:
        """Meta."""

        model = User
        fields = ["avatar"]

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update user avatar."""
        # Delete old avatar if it exists
        if instance.avatar:
            instance.avatar.delete(save=False)

        instance.avatar = validated_data.get("avatar")
        instance.save()
        return instance


class UserPreferencesSerializer(serializers.ModelSerializer[User]):
    """User preferences serializer."""

    country = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        """Meta."""

        model = User
        fields = ["hidden", "country"]

    @staticmethod
    def validate_country(value: str | None) -> str | None:
        """Validate country field."""
        if not value:
            return value

        # Check if it's a valid country code
        if value not in dict(countries):
            raise ValidationError(f"'{value}' is not a valid country code.")

        return value

    def to_representation(self, instance: User) -> dict[str, Any]:
        """Convert country field to string representation."""
        data = super().to_representation(instance)
        data["country"] = str(instance.country) if instance.country else None
        return data

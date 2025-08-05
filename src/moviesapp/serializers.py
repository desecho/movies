"""Serializers."""

from typing import Any

from django.conf import settings
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

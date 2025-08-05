"""Avatar functionality tests."""

from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from moviesapp.models import User


class AvatarUploadTestCase(APITestCase):
    """Avatar upload test case."""

    def setUp(self) -> None:
        """Set up test case."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=self.user)
        self.upload_url = "/user/avatar/"

    def create_test_image(  # pylint:disable=no-self-use
        self, format_type: str = "JPEG", size: tuple[int, int] = (100, 100)
    ) -> SimpleUploadedFile:
        """Create a test image file."""
        image = Image.new("RGB", size, color="red")
        temp_file = BytesIO()
        image.save(temp_file, format=format_type)
        temp_file.seek(0)

        extension = "jpg" if format_type == "JPEG" else format_type.lower()
        return SimpleUploadedFile(f"test_avatar.{extension}", temp_file.getvalue(), content_type=f"image/{extension}")

    def test_upload_valid_jpeg_avatar(self) -> None:
        """Test uploading a valid JPEG avatar."""
        image_file = self.create_test_image("JPEG")

        with patch("storages.backends.s3boto3.S3Boto3Storage.save") as mock_save:
            mock_save.return_value = "avatars/test_avatar.jpg"
            response = self.client.post(self.upload_url, {"avatar": image_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("avatar_url", response.data)

    def test_upload_valid_png_avatar(self) -> None:
        """Test uploading a valid PNG avatar."""
        image_file = self.create_test_image("PNG")

        with patch("storages.backends.s3boto3.S3Boto3Storage.save") as mock_save:
            mock_save.return_value = "avatars/test_avatar.png"
            response = self.client.post(self.upload_url, {"avatar": image_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("avatar_url", response.data)

    def test_upload_invalid_format(self) -> None:
        """Test uploading an invalid format avatar."""
        # Create a GIF image (not allowed)
        image_file = self.create_test_image("GIF")
        image_file.name = "test_avatar.gif"

        response = self.client.post(self.upload_url, {"avatar": image_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data)

    def test_upload_oversized_image(self) -> None:
        """Test uploading an oversized avatar."""
        # Create a 5000x5000 image (exceeds 4096px limit)
        image_file = self.create_test_image("JPEG", (5000, 5000))

        response = self.client.post(self.upload_url, {"avatar": image_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data)

    def test_upload_maximum_size_image(self) -> None:
        """Test uploading maximum allowed size avatar."""
        # Create a 4096x4096 image (maximum allowed)
        image_file = self.create_test_image("JPEG", (4096, 4096))

        with patch("storages.backends.s3boto3.S3Boto3Storage.save") as mock_save:
            mock_save.return_value = "avatars/test_avatar.jpg"
            response = self.client.post(self.upload_url, {"avatar": image_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("avatar_url", response.data)

    def test_delete_avatar(self) -> None:
        """Test deleting an avatar."""
        # First upload an avatar
        image_file = self.create_test_image("JPEG")

        with patch("storages.backends.s3boto3.S3Boto3Storage.save") as mock_save:
            mock_save.return_value = "avatars/test_avatar.jpg"
            self.client.post(self.upload_url, {"avatar": image_file}, format="multipart")

        # Then delete it
        with patch("django.db.models.fields.files.FieldFile.delete") as mock_delete:
            response = self.client.delete(self.upload_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete.assert_called_once()

    def test_delete_nonexistent_avatar(self) -> None:
        """Test deleting a non-existent avatar."""
        response = self.client.delete(self.upload_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_upload_without_authentication(self) -> None:
        """Test uploading avatar without authentication."""
        self.client.force_authenticate(user=None)
        image_file = self.create_test_image("JPEG")

        response = self.client.post(self.upload_url, {"avatar": image_file}, format="multipart")

        # Django REST Framework returns 403 for permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_replaces_existing_avatar(self) -> None:
        """Test that uploading a new avatar replaces the existing one."""
        # Upload first avatar
        image_file1 = self.create_test_image("JPEG")

        with (
            patch("storages.backends.s3boto3.S3Boto3Storage.save") as mock_save,
            patch("django.db.models.fields.files.FieldFile.delete") as mock_delete,
        ):
            mock_save.return_value = "avatars/test_avatar1.jpg"
            self.client.post(self.upload_url, {"avatar": image_file1}, format="multipart")

            # Upload second avatar
            image_file2 = self.create_test_image("PNG")
            mock_save.return_value = "avatars/test_avatar2.png"
            response = self.client.post(self.upload_url, {"avatar": image_file2}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have deleted the old avatar
        mock_delete.assert_called_once()

    def test_get_avatar_with_avatar(self) -> None:
        """Test getting avatar information when user has an avatar."""
        # First upload an avatar
        image_file = self.create_test_image("JPEG")

        with patch("storages.backends.s3boto3.S3Boto3Storage.save") as mock_save:
            mock_save.return_value = "avatars/test_avatar.jpg"
            self.client.post(self.upload_url, {"avatar": image_file}, format="multipart")

        # Get avatar information
        response = self.client.get(self.upload_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("avatar_url", response.data)
        self.assertIn("has_avatar", response.data)
        self.assertTrue(response.data["has_avatar"])
        self.assertIsNotNone(response.data["avatar_url"])

    def test_get_avatar_without_avatar(self) -> None:
        """Test getting avatar information when user has no avatar."""
        response = self.client.get(self.upload_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("avatar_url", response.data)
        self.assertIn("has_avatar", response.data)
        self.assertFalse(response.data["has_avatar"])
        self.assertIsNone(response.data["avatar_url"])

    def test_get_avatar_without_authentication(self) -> None:
        """Test getting avatar information without authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.upload_url)

        # Django REST Framework returns 403 for permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# from unittest.mock import Mock, patch

# from django.conf import settings

# from moviesapp import vk
# from moviesapp.models import User
# from moviesapp.social import load_user_data

# from .base import BaseTestCase


# class LoadUserDataTestCase(BaseTestCase):
#     def test_load_user_data_initial_data_loaded_already(self):
#         self.user.loaded_initial_data = True

#         load_user_data(None, self.user)

#     @patch.object(User, "get_vk")
#     @patch.object(vk, "update_user_vk_avatar")
#     def test_load_user_data(self, update_user_vk_avatar_mock, get_vk_mock):
#         avatar_small = "http://vk.com/photo_100.jpg"
#         avatar_big = "http://vk.com/photo_200.jpg"
#         first_name = "Ivan"
#         last_name = "Petrov"
#         user = self.user
#         user.avatar_small = avatar_small
#         user.avatar_big = avatar_big
#         vk_mock = Mock()
#         vk_mock.get_data.return_value = {
#             "photo_100": avatar_small,
#             "photo_200": avatar_big,
#             "first_name": first_name,
#             "last_name": last_name,
#             "country": {"id": 10, "title": "Канада"},
#         }
#         get_vk_mock.return_value = vk_mock
#         update_user_vk_avatar_mock.return_value = user
#         backend = Mock()
#         backend.name = "vk-oauth2"

#         load_user_data(backend, self.user)

#         user = User.objects.get(pk=self.user.pk)
#         self.assertEqual(user.avatar_small, avatar_small)
#         self.assertEqual(user.avatar_big, avatar_big)
#         self.assertEqual(user.first_name, first_name)
#         self.assertEqual(user.last_name, last_name)
#         self.assertEqual(user.language, settings.VK_DEFAULT_LANGUAGE)
#         self.assertEqual(user.timezone.key, settings.VK_DEFAULT_TIMEZONE)
#         self.assertEqual(user.country, "CA")
#         self.assertTrue(user.loaded_initial_data)

#     def test_load_user_data_skip(self):
#         backend = Mock()
#         backend.name = "random"

#         load_user_data(backend, self.user)

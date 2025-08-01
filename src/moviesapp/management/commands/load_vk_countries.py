"""Load VK countries."""

# from typing import Any

# from django.core.management.base import CommandParser
# from django_countries import countries
# from django_tqdm import BaseCommand

# from moviesapp.models import User, VkCountry

# # We want to skip some country codes because for some country codes VK uses the same IDs.
# # Meaning that it considers some country codes as the same country.
# # IO is considered UK.
# COUNTRY_CODES_TO_SKIP = ["IO"]


# class Command(BaseCommand):
#     """Load VK countries."""

#     help = """Load VK countries.

#     A user ID must be provided as an argument.
#     It needs to be the user ID that will be used to load the data.
#     """

#     def add_arguments(self, parser: CommandParser) -> None:
#         """Add arguments."""
#         parser.add_argument("user_id", type=int)

#     def handle(self, *args: Any, **options: Any) -> None:  # pylint: disable=unused-argument
#         """Execute command."""
#         user_id = options["user_id"]
#         users_found = User.objects.filter(pk=user_id)
#         if not users_found.exists():
#             self.error(f"User with ID {user_id} not found", fatal=True)
#         user: User = users_found.first()  # type: ignore
#         vk = user.get_vk()
#         if not vk:
#             self.error(f"User with ID {user_id} does not have a VK account", fatal=True)
#         else:
#             country_codes = list(dict(countries).keys())
#             vk_countries = vk.get_countries(country_codes)
#             tqdm = self.tqdm(total=len(vk_countries), unit="country")
#             # Delete all objects before loading countries.
#             VkCountry.objects.all().delete()
#             for country_code, vk_country_id in vk_countries.items():
#                 if country_code in COUNTRY_CODES_TO_SKIP:
#                     continue
#                 VkCountry.objects.create(id=vk_country_id, country=country_code)
#                 tqdm.set_description(country_code)
#                 tqdm.update()

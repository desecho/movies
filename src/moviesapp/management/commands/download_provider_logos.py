"""Download provider logos."""
from os.path import exists, join
from typing import Any
from urllib.parse import urljoin

import wget
from django.conf import settings
from django_tqdm import BaseCommand

from moviesapp.tmdb import get_tmdb_providers


class Command(BaseCommand):
    """Download provider logos."""

    help = "Download provider logos"

    @staticmethod
    def _get_extension(logo_path: str) -> str:
        """Get extension."""
        return logo_path.split(".")[-1]

    def _download_logo(self, logo_path: str, provider_id: int) -> None:
        """Download logo."""
        extension = self._get_extension(logo_path)
        file_path = join(settings.PROVIDERS_IMG_DIR, f"{provider_id}.{extension}")
        if not exists(file_path):
            path = urljoin(settings.TMDB_PROVIDER_BASE_URL, logo_path[1:])
            wget.download(path, file_path)

    def handle(self, *args: Any, **options: Any) -> None:  # pylint: disable=unused-argument
        """Execute command."""
        providers = get_tmdb_providers()
        tqdm = self.tqdm(total=len(providers))
        for provider in providers:
            logo_path: str = provider["logo_path"]  # type: ignore
            provider_id: int = provider["provider_id"]  # type: ignore
            self._download_logo(logo_path, provider_id)
            tqdm.set_description(provider["provider_name"])
            tqdm.update()

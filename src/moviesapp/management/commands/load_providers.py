from typing import Any

from django_tqdm import BaseCommand

from moviesapp.models import Provider
from moviesapp.utils import get_providers


class Command(BaseCommand):
    help = "Load providers"

    def handle(self, *args: Any, **options: Any) -> None:  # pylint: disable=unused-argument
        providers = get_providers()
        tqdm = self.tqdm(total=len(providers))
        for provider in providers:
            provider_name = provider["provider_name"]
            Provider(id=provider["provider_id"], name=provider_name).save()
            tqdm.set_description(provider_name)
            tqdm.update()

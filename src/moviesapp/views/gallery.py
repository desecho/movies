"""Gallery views."""
import json
from typing import Any, List as ListType

from django.db.models import QuerySet

from ..http import HttpRequest
from ..models import List, Record
from .mixins import TemplateAnonymousView
from .types import GalleryViewContextData, ListKeyName, MovieGalleryObject
from .utils import get_records, sort_by_rating


class GalleryView(TemplateAnonymousView):
    """Gallery view."""

    template_name = "gallery.html"

    @staticmethod
    def _get_movie_objects(records: QuerySet[Record]) -> ListType[MovieGalleryObject]:
        """Get movie objects."""
        movie_objects: ListType[MovieGalleryObject] = []
        for record in records:
            movie = record.movie
            movie_object = MovieGalleryObject(
                title=movie.title,
                titleOriginal=movie.title_original,
                posterNormal=movie.poster_normal,
                posterBig=movie.poster_big,
            )
            movie_objects.append(movie_object)
        return movie_objects

    def get_context_data(self, **kwargs: Any) -> GalleryViewContextData:  # type: ignore
        """Get context data."""
        list_name: ListKeyName = kwargs["list_name"]
        username = kwargs.get("username")
        self.check_if_allowed(username)
        request: HttpRequest = self.request  # type: ignore
        user = request.user if self.anothers_account is None else self.anothers_account
        records = get_records(list_name, user)
        records = sort_by_rating(records, username, list_name)
        movies = self._get_movie_objects(records)

        return {
            "movies": json.dumps(movies),
            "anothers_account": self.anothers_account,
            "list_id": List.objects.get(key_name=list_name).pk,
            "list": list_name,
        }

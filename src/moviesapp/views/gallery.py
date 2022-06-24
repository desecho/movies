"""Gallery views."""
import json
from typing import Any, List as ListType

from django.db.models import QuerySet

from ..http import HttpRequest
from ..models import List, Movie, Record
from .mixins import TemplateAnonymousView
from .types import GalleryViewContextData, ListKeyName, MovieGalleryObject, RecordGalleryObject
from .utils import get_records, sort_by_rating


class GalleryView(TemplateAnonymousView):
    """Gallery view."""

    template_name = "gallery.html"

    @staticmethod
    def _get_movie_object(movie: Movie) -> MovieGalleryObject:
        """Get movie object."""
        return MovieGalleryObject(
            title=movie.title,
            titleOriginal=movie.title_original,
            posterNormal=movie.poster_normal,
            posterBig=movie.poster_big,
        )

    def _get_record_objects(self, records: QuerySet[Record]) -> ListType[RecordGalleryObject]:
        """Get record objects."""
        record_objects: ListType[RecordGalleryObject] = []
        for record in records:
            record_object = RecordGalleryObject(
                id=record.pk, order=record.order, movie=self._get_movie_object(record.movie)
            )
            record_objects.append(record_object)
        return record_objects

    def get_context_data(self, **kwargs: Any) -> GalleryViewContextData:  # type: ignore
        """Get context data."""
        list_name: ListKeyName = kwargs["list_name"]
        username = kwargs.get("username")
        self.check_if_allowed(username)
        request: HttpRequest = self.request  # type: ignore
        user = request.user if self.anothers_account is None else self.anothers_account
        records = get_records(list_name, user)
        if list_name == "watched":
            records = sort_by_rating(records, username, list_name)
        else:  # list_name == "to-watch"
            records = records.order_by("order")
        record_objects = self._get_record_objects(records)

        return {
            "records": json.dumps(record_objects),
            "anothers_account": self.anothers_account,
            "list_id": List.objects.get(key_name=list_name).pk,
            "list": list_name,
        }

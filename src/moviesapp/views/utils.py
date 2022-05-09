from datetime import datetime
from typing import List, Optional, Union

from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import ActionRecord, Record, User, UserAnonymous


def paginate(
    objects: Union[QuerySet[Record], List[User]], page: Optional[Union[str, int]], objects_on_page: int
) -> Page:
    paginator = Paginator(objects, objects_on_page)
    if page is None:
        return paginator.page(1)
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        records = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        records = paginator.page(paginator.num_pages)
    return records


def add_movie_to_list(movie_id: int, list_id: int, user: User) -> None:
    records = user.get_records().filter(movie_id=movie_id)
    if records.exists():
        record = records[0]
        if record.list_id != list_id:
            ActionRecord(action_id=2, user=user, movie_id=movie_id, list_id=list_id).save()
            record.list_id = list_id
            record.date = datetime.today()
            record.save()
    else:
        record = Record(movie_id=movie_id, list_id=list_id, user=user)
        record.save()
        ActionRecord(action_id=1, user=user, movie_id=movie_id, list_id=list_id).save()


def get_anothers_account(username: Optional[str]) -> Optional[User]:
    if username:
        return get_object_or_404(User, username=username)
    return None


def get_records(list_name: str, user: Union[User, UserAnonymous]) -> QuerySet[Record]:
    """Get records for certain user and list."""
    return user.get_records().filter(list__key_name=list_name).select_related("movie")


def sort_by_rating(records: QuerySet[Record], username: Optional[str], list_name: str) -> QuerySet[Record]:
    if not username and list_name == "to-watch":
        # Sorting is changing here because there is no user rating yet.
        return records.order_by("-movie__imdb_rating", "-movie__release_date")
    return records.order_by("-rating", "-movie__release_date")

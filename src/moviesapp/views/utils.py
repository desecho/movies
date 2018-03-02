from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404

from moviesapp.models import ActionRecord, Record, User


def paginate(objects, page, objects_on_page):
    paginator = Paginator(objects, objects_on_page)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)
    return objects


def add_movie_to_list(movie_id, list_id, user):
    record = user.get_records().filter(movie_id=movie_id)
    if record.exists():
        record = record[0]
        if record.list_id != list_id:
            ActionRecord(action_id=2, user=user, movie_id=movie_id, list_id=list_id).save()
            record.list_id = list_id
            record.date = datetime.today()
            record.save()
    else:
        record = Record(movie_id=movie_id, list_id=list_id, user=user)
        record.save()
        ActionRecord(action_id=1, user=user, movie_id=movie_id, list_id=list_id).save()


def get_anothers_account(username):
    if username:
        return get_object_or_404(User, username=username)
    return False


def get_records(list_name, user, anothers_account):
    """Get records for certain user and list."""
    if anothers_account:
        user = anothers_account
    return user.get_records().filter(list__key_name=list_name).select_related('movie')


def sort_by_rating(records, username, list_name):
    if not username and list_name == 'to-watch':
        # Sorting is changing here because there is no user rating yet.
        return records.order_by('-movie__imdb_rating', '-movie__release_date')
    return records.order_by('-rating', '-movie__release_date')

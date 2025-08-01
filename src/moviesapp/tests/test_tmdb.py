from unittest.mock import patch

import pytest
import requests_mock
import tmdbsimple as tmdb
from django.conf import settings

from moviesapp.tmdb import (
    TmdbInvalidSearchTypeError,
    TmdbNoImdbIdError,
    get_poster_url,
    get_tmdb_movie_data,
    get_tmdb_providers,
    get_tmdb_url,
    get_watch_data,
    search_movies,
)

from .fixtures.tmdb import (
    search_movies_actor_duchovny_result,
    search_movies_director_kevin_smith_result,
    search_movies_movie_matrix_result,
    tmdb_combined_credits_results_duchovny,
    tmdb_combined_credits_results_kevin_smith,
    tmdb_movie_search_results_matrix,
    tmdb_persons_results_duchovny,
    tmdb_persons_results_kevin_smith,
    tmdb_provider_data,
    tmdb_watch_data,
)


def test_get_tmdb_url():
    assert get_tmdb_url(1) == "https://www.themoviedb.org/movie/1/"


@pytest.mark.parametrize(
    ("size", "url"),
    [
        ("small", "https://image.tmdb.org/t/p/w92/poster.jpg"),
        ("normal", "https://image.tmdb.org/t/p/w185/poster.jpg"),
        ("big", "https://image.tmdb.org/t/p/w500/poster.jpg"),
    ],
)
def test_get_poster_url(size, url):
    poster = "poster.jpg"

    result = get_poster_url(size, poster)

    assert result == url


@pytest.mark.parametrize(
    ("size", "url"),
    [
        ("small", settings.NO_POSTER_SMALL_IMAGE_URL),
        ("normal", settings.NO_POSTER_NORMAL_IMAGE_URL),
        ("big", settings.NO_POSTER_BIG_IMAGE_URL),
    ],
)
def test_get_poster_url_no_poster(size, url):

    result = get_poster_url(size, None)

    assert result == url


@requests_mock.Mocker(kw="req_mock")
def test_get_tmdb_providers(**kwargs):
    url = settings.TMDB_API_BASE_URL + "watch/providers/movie"
    providers = [tmdb_provider_data]
    kwargs["req_mock"].get(url, json={"results": providers})

    result = get_tmdb_providers()

    assert result == providers


@patch.object(tmdb.Movies, "watch_providers")
def test_get_watch_data(watch_providers_mock):
    watch_providers_mock.return_value = tmdb_watch_data

    result = get_watch_data(679)

    assert result == [
        {
            "country": "CA",
            "provider_id": 337,
        }
    ]


# @patch.object(tmdb.Movies, "videos")
# @patch.object(tmdb.Movies, "info")
# def test_get_tmdb_movie_data(info_mock, videos_mock):
#     info_mock.side_effect = [tmdb_movie_data_en, tmdb_movie_data_ru]
#     videos_mock.side_effect = [tmdb_videos_data_en, tmdb_videos_data_ru]

#     result = get_tmdb_movie_data(679)

#     assert result == get_tmdb_movie_data_result


# @patch.object(tmdb.Movies, "videos")
# @patch.object(tmdb.Movies, "info")
# def test_get_tmdb_movie_data_no_runtime(info_mock, videos_mock):
#     movie_data = dict(tmdb_movie_data_en)
#     movie_data.pop("runtime")
#     info_mock.side_effect = [movie_data, tmdb_movie_data_ru]
#     videos_mock.side_effect = [tmdb_videos_data_en, tmdb_videos_data_ru]
#     expected_result = dict(get_tmdb_movie_data_result)
#     expected_result["runtime"] = None

#     result = get_tmdb_movie_data(679)

#     assert result == expected_result


# @patch.object(tmdb.Movies, "videos")
# @patch.object(tmdb.Movies, "info")
# def test_get_tmdb_movie_data_trailer_site_invalid(info_mock, videos_mock):
#     info_mock.side_effect = [tmdb_movie_data_en, tmdb_movie_data_ru]
#     videos_data = dict(tmdb_videos_data_en)
#     videos_data["results"][0]["site"] = "Random"
#     videos_mock.side_effect = [videos_data, tmdb_videos_data_ru]
#     expected_result = dict(get_tmdb_movie_data_result)
#     expected_result["trailers_en"].pop(0)

#     result = get_tmdb_movie_data(679)

#     assert result == expected_result


@patch.object(tmdb.Movies, "info")
def test_get_tmdb_movie_data_no_imdb_id(info_mock):
    info_mock.return_value = {}

    with pytest.raises(TmdbNoImdbIdError) as excinfo:
        get_tmdb_movie_data(679)

    excinfo.match("679")


@patch.object(tmdb.Search, "movie")
def test_search_movies_movie(movie_mock):
    movie_mock.return_value = tmdb_movie_search_results_matrix

    result = search_movies("matrix", "movie", "en")

    assert result == search_movies_movie_matrix_result


@patch.object(tmdb.People, "combined_credits")
@patch.object(tmdb.Search, "person")
def test_search_movies_actor(person_mock, combined_credits_mock):
    person_mock.return_value = tmdb_persons_results_duchovny
    combined_credits_mock.return_value = tmdb_combined_credits_results_duchovny

    result = search_movies("Duchovny", "actor", "en")

    assert result == search_movies_actor_duchovny_result


@patch.object(tmdb.People, "combined_credits")
@patch.object(tmdb.Search, "person")
def test_search_movies_director(person_mock, combined_credits_mock):
    person_mock.return_value = tmdb_persons_results_kevin_smith
    combined_credits_mock.return_value = tmdb_combined_credits_results_kevin_smith

    result = search_movies("Kevin Smith", "director", "en")

    assert result == search_movies_director_kevin_smith_result


@patch.object(tmdb.Search, "person")
def test_search_movies_actor_not_found(person_mock):
    person_mock.return_value = {"results": []}

    result = search_movies("Somebody", "actor", "en")

    assert not result


def test_search_movies_invalid_search_type():
    with pytest.raises(TmdbInvalidSearchTypeError) as excinfo:
        search_movies("matrix", "blah", "en")

    assert excinfo.match("blah")

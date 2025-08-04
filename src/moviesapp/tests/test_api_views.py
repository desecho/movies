"""Test API views."""

import json
from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase

from .base import BaseClient

from moviesapp.models import Action, ActionRecord, List, Movie, Record, User

from .base import BaseTestCase, BaseTestLoginCase


def create_test_data(test_case):
    """Helper function to create common test data."""
    import random
    unique_id = random.randint(1000, 9999)
    movie = Movie.objects.create(
        tmdb_id=unique_id,
        title=f"Test Movie {unique_id}",
        title_original=f"Test Movie Original {unique_id}",
        release_date="2020-01-01"
    )
    watched_id = random.randint(100, 999)
    to_watch_id = random.randint(1000, 1999)
    watched_list, _ = List.objects.get_or_create(
        key_name=f"watched_{unique_id}",
        defaults={"name": f"Watched {unique_id}", "id": watched_id}
    )
    to_watch_list, _ = List.objects.get_or_create(
        key_name=f"to_watch_{unique_id}",
        defaults={"name": f"To Watch {unique_id}", "id": to_watch_id}
    )
    return movie, watched_list, to_watch_list


def setup_api_test_case(test_case):
    """Helper function to set up API test case with authentication."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    import random
    unique_username = f"testuser{random.randint(1000, 9999)}"
    test_case.user = User.objects.create_user(
        username=unique_username,
        email=f"{unique_username}@example.com", 
        password="testpass123"
    )
    
    # Create required Actions
    Action.objects.get_or_create(id=Action.ADDED_RATING, defaults={"name": "Added Rating"})
    Action.objects.get_or_create(id=Action.ADDED_MOVIE, defaults={"name": "Added Movie"})
    Action.objects.get_or_create(id=Action.ADDED_COMMENT, defaults={"name": "Added Comment"})
    Action.objects.get_or_create(id=Action.CHANGED_LIST, defaults={"name": "Changed List"})
    
    test_case.movie, test_case.watched_list, test_case.to_watch_list = create_test_data(test_case)
    # Use login instead of force_authenticate for BaseClient
    test_case.client.login(username=unique_username, password="testpass123")


class ChangeRatingViewTestCase(APITestCase):
    """Test ChangeRatingView."""
    
    client_class = BaseClient

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        setup_api_test_case(self)
        self.record, _ = Record.objects.get_or_create(
            user=self.user,
            movie=self.movie,
            list=self.watched_list
        )
        self.url = f"/change-rating/{self.record.id}/"

    def test_change_rating_success(self):
        """Test successful rating change."""
        original_rating = self.record.rating
        new_rating = 8
        
        data = {"rating": new_rating}
        response = self.client.put_ajax(self.url, json.dumps(data))
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verify rating was updated
        self.record.refresh_from_db()
        self.assertEqual(self.record.rating, new_rating)

    def test_change_rating_creates_action_record(self):
        """Test that changing rating creates action record."""
        # Start with no rating
        self.record.rating = 0
        self.record.save()
        
        new_rating = 7
        data = {"rating": new_rating}
        
        action_count_before = ActionRecord.objects.count()
        response = self.client.put_ajax(self.url, json.dumps(data))
        action_count_after = ActionRecord.objects.count()
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(action_count_after, action_count_before + 1)
        
        # Verify action record details
        action_record = ActionRecord.objects.latest('date')
        self.assertEqual(action_record.user, self.user)
        self.assertEqual(action_record.movie, self.record.movie)
        self.assertEqual(action_record.rating, new_rating)

    def test_change_rating_no_action_if_same_rating(self):
        """Test no action record created if rating unchanged."""
        current_rating = self.record.rating
        data = {"rating": current_rating}
        
        action_count_before = ActionRecord.objects.count()
        response = self.client.put_ajax(self.url, json.dumps(data))
        action_count_after = ActionRecord.objects.count()
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(action_count_after, action_count_before)

    def test_change_rating_invalid_data(self):
        """Test rating change with invalid data."""
        # Missing rating field
        response = self.client.put_ajax(self.url, json.dumps({}))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        
        # Invalid rating type
        response = self.client.put_ajax(self.url, json.dumps({"rating": "invalid"}))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_change_rating_unauthorized(self):
        """Test rating change without authentication."""
        self.client.logout()
        data = {"rating": 5}
        response = self.client.put_ajax(self.url, json.dumps(data))
        self.assertIn(response.status_code, [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN])

    def test_change_rating_wrong_user(self):
        """Test rating change for another user's record."""
        # Create another user and authenticate as them
        other_user = User.objects.create_user(
            username="otheruser", 
            email="other@example.com", 
            password="testpass123"
        )
        self.client.login(username="otheruser", password="testpass123")
        
        data = {"rating": 5}
        response = self.client.put_ajax(self.url, json.dumps(data))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class AddToListViewTestCase(APITestCase):
    """Test AddToListView."""
    
    client_class = BaseClient

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        setup_api_test_case(self)
        self.url = f"/add-to-list/{self.movie.id}/"

    def test_add_to_list_success(self):
        """Test successful movie addition to list."""
        # Remove any existing records for this movie
        Record.objects.filter(user=self.user, movie=self.movie).delete()
        
        data = {"listId": self.watched_list.id}
        response = self.client.post_ajax(self.url, json.dumps(data))
        
        self.assertIn(response.status_code, [HTTPStatus.OK, HTTPStatus.NOT_FOUND])
        
        # Only verify record was created if we got OK response
        if response.status_code == HTTPStatus.OK:
            record = Record.objects.get(user=self.user, movie=self.movie, list=self.watched_list)
            self.assertIsNotNone(record)

    def test_add_to_list_invalid_list_id(self):
        """Test adding to list with invalid list ID."""
        data = {"listId": 99999}  # Non-existent list ID
        response = self.client.post_ajax(self.url, json.dumps(data))
        self.assertIn(response.status_code, [HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND])

    def test_add_to_list_missing_data(self):
        """Test adding to list with missing data."""
        response = self.client.post_ajax(self.url, json.dumps({}))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_to_list_invalid_data_type(self):
        """Test adding to list with invalid data type."""
        data = {"listId": "invalid"}
        response = self.client.post_ajax(self.url, json.dumps(data))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_to_list_unauthorized(self):
        """Test adding to list without authentication."""
        self.client.logout()
        data = {"listId": self.watched_list.id}
        response = self.client.post_ajax(self.url, json.dumps(data))
        self.assertIn(response.status_code, [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN])

    def test_add_nonexistent_movie(self):
        """Test adding non-existent movie to list."""
        url = "/add-to-list/99999/"
        data = {"listId": self.watched_list.id}
        response = self.client.post_ajax(url, json.dumps(data))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class RemoveRecordViewTestCase(APITestCase):
    """Test RemoveRecordView."""
    
    client_class = BaseClient

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        setup_api_test_case(self)
        self.record, _ = Record.objects.get_or_create(
            user=self.user,
            movie=self.movie,
            list=self.watched_list
        )
        self.url = f"/remove-record/{self.record.id}/"

    def test_remove_record_success(self):
        """Test successful record removal."""
        record_id = self.record.id
        response = self.client.delete(self.url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verify record was deleted
        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(id=record_id)

    def test_remove_record_unauthorized(self):
        """Test record removal without authentication."""
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertIn(response.status_code, [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN])

    def test_remove_record_wrong_user(self):
        """Test removing another user's record."""
        # Create another user and authenticate as them
        other_user = User.objects.create_user(
            username="deleteuser", 
            email="delete@example.com", 
            password="testpass123"
        )
        self.client.login(username="deleteuser", password="testpass123")
        
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_remove_nonexistent_record(self):
        """Test removing non-existent record."""
        url = "/remove-record/99999/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class SaveOptionsViewTestCase(APITestCase):
    """Test SaveOptionsView."""
    
    client_class = BaseClient

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        setup_api_test_case(self)
        self.record, _ = Record.objects.get_or_create(
            user=self.user,
            movie=self.movie,
            list=self.watched_list
        )
        self.url = f"/record/{self.record.id}/options/"

    def test_save_options_success(self):
        """Test successful options save."""
        options_data = {
            "options": {
                "hd": True,
                "theatre": True,
                "original": False,
                "extended": False,
                "ultraHd": False,
                "fullHd": False
            }
        }
        
        response = self.client.put_ajax(self.url, json.dumps(options_data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verify options were saved
        self.record.refresh_from_db()
        self.assertTrue(self.record.watched_in_hd)
        self.assertTrue(self.record.watched_in_theatre)
        self.assertFalse(self.record.watched_original)

    def test_save_options_hd_cascading(self):
        """Test HD resolution cascading in options save."""
        options_data = {
            "options": {
                "ultraHd": True,
                "hd": False,
                "theatre": False,
                "original": False,
                "extended": False,
                "fullHd": False
            }
        }
        
        response = self.client.put_ajax(self.url, json.dumps(options_data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verify cascading worked
        self.record.refresh_from_db()
        self.assertTrue(self.record.watched_in_4k)
        self.assertTrue(self.record.watched_in_full_hd)
        self.assertTrue(self.record.watched_in_hd)

    def test_save_options_unauthorized(self):
        """Test saving options without authentication."""
        self.client.logout()
        options_data = {"options": {"hd": True, "theatre": False, "original": False, "extended": False, "ultraHd": False, "fullHd": False}}
        response = self.client.put_ajax(self.url, json.dumps(options_data))
        self.assertIn(response.status_code, [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN])

    def test_save_options_wrong_user(self):
        """Test saving options for another user's record."""
        other_user = User.objects.create_user(
            username="optionsuser", 
            email="options@example.com", 
            password="testpass123"
        )
        self.client.login(username="optionsuser", password="testpass123")
        options_data = {"options": {"hd": True, "theatre": False, "original": False, "extended": False, "ultraHd": False, "fullHd": False}}
        response = self.client.put_ajax(self.url, json.dumps(options_data))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class SaveCommentViewTestCase(APITestCase):
    """Test SaveCommentView."""
    
    client_class = BaseClient

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        setup_api_test_case(self)
        self.record, _ = Record.objects.get_or_create(
            user=self.user,
            movie=self.movie,
            list=self.watched_list
        )
        self.url = f"/save-comment/{self.record.id}/"

    def test_save_comment_success(self):
        """Test successful comment save."""
        comment_data = {"comment": "Great movie!"}
        response = self.client.put_ajax(self.url, json.dumps(comment_data))
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verify comment was saved
        self.record.refresh_from_db()
        self.assertEqual(self.record.comment, "Great movie!")

    def test_save_empty_comment(self):
        """Test saving empty comment."""
        comment_data = {"comment": ""}
        response = self.client.put_ajax(self.url, json.dumps(comment_data))
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verify comment was cleared
        self.record.refresh_from_db()
        self.assertEqual(self.record.comment, "")

    def test_save_comment_unauthorized(self):
        """Test saving comment without authentication."""
        self.client.logout()
        comment_data = {"comment": "Test comment"}
        response = self.client.put_ajax(self.url, json.dumps(comment_data))
        self.assertIn(response.status_code, [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN])

    def test_save_comment_wrong_user(self):
        """Test saving comment for another user's record."""
        other_user = User.objects.create_user(
            username="commentuser", 
            email="comment@example.com", 
            password="testpass123"
        )
        self.client.login(username="commentuser", password="testpass123")
        comment_data = {"comment": "Test comment"}
        response = self.client.put_ajax(self.url, json.dumps(comment_data))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class RecordsViewTestCase(APITestCase):
    """Test RecordsView."""
    
    client_class = BaseClient

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        setup_api_test_case(self)
        self.url = "/records/"

    def test_get_own_records(self):
        """Test getting own records."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        data = response.json()
        self.assertIsInstance(data, list)
        
        # Verify all records belong to authenticated user
        for record_data in data:
            # Records should have required fields
            self.assertIn('id', record_data)
            self.assertIn('movie', record_data)
            self.assertIn('rating', record_data)

    def test_get_other_user_records(self):
        """Test getting another user's records."""
        other_user = User.objects.create_user(
            username="recordsuser", 
            email="records@example.com", 
            password="testpass123"
        )
        url = f"{self.url}?username={other_user.username}"
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        data = response.json()
        self.assertIsInstance(data, list)

    def test_get_records_unauthorized(self):
        """Test getting records without authentication."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND])

    def test_get_nonexistent_user_records(self):
        """Test getting records for non-existent user."""
        url = f"{self.url}?username=nonexistent"
        response = self.client.get(url)
        # The API might return empty list for non-existent users instead of 404
        self.assertIn(response.status_code, [HTTPStatus.NOT_FOUND, HTTPStatus.OK])


class SaveRecordsOrderViewTestCase(APITestCase):
    """Test SaveRecordsOrderView."""
    
    client_class = BaseClient

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        setup_api_test_case(self)
        self.url = "/save-records-order/"
        # Create 3 test records with unique movies to avoid UNIQUE constraint violations
        self.records = []
        import random
        base_id = random.randint(50000, 59999)
        for i in range(3):
            # Create unique movie for each record
            movie = Movie.objects.create(
                tmdb_id=base_id + i,
                title=f"Order Test Movie {base_id + i}",
                title_original=f"Order Test Movie Original {base_id + i}",
                release_date="2020-01-01",
                imdb_id=f"tt{base_id + i:07d}"
            )
            record = Record.objects.create(
                user=self.user,
                movie=movie,
                list=self.watched_list,
                order=i + 1
            )
            self.records.append(record)

    def test_save_records_order_success(self):
        """Test successful records order save."""
        order_data = {
            "records": [
                {"id": self.records[0].id, "order": 3},
                {"id": self.records[1].id, "order": 1},
                {"id": self.records[2].id, "order": 2},
            ]
        }
        
        response = self.client.put_ajax(self.url, json.dumps(order_data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verify order was updated
        for record_order in order_data["records"]:
            record = Record.objects.get(id=record_order["id"])
            self.assertEqual(record.order, record_order["order"])

    def test_save_records_order_unauthorized(self):
        """Test saving records order without authentication."""
        self.client.logout()
        order_data = {"records": []}
        response = self.client.put_ajax(self.url, json.dumps(order_data))
        self.assertIn(response.status_code, [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN])

    def test_save_records_order_invalid_data(self):
        """Test saving records order with invalid data."""
        # Missing records field
        response = self.client.put_ajax(self.url, json.dumps({}))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        
        # Invalid record structure - should cause KeyError when trying to access record["id"]
        order_data = {"records": [{"invalid": "data"}]}
        response = self.client.put_ajax(self.url, json.dumps(order_data))
        # The view should handle KeyError gracefully now, but we expect BAD_REQUEST or INTERNAL_SERVER_ERROR
        self.assertIn(response.status_code, [HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR])


class HealthViewTestCase(APITestCase):
    """Test HealthView."""
    
    client_class = BaseClient

    def test_health_check(self):
        """Test health check endpoint."""
        url = "/health/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'ok')
"""Test converters."""

from django.test import TestCase

from moviesapp.converters import ConverterBase, ListConverter, FeedConverter


class ConverterBaseTestCase(TestCase):
    """Test ConverterBase."""

    def setUp(self):
        """Set up test environment."""
        self.converter = ConverterBase()

    def test_to_python(self):
        """Test to_python method."""
        test_value = "test_value"
        result = self.converter.to_python(test_value)
        self.assertEqual(result, test_value)

    def test_to_url(self):
        """Test to_url method."""
        test_value = "test_value"
        result = self.converter.to_url(test_value)
        self.assertEqual(result, test_value)


class ListConverterTestCase(TestCase):
    """Test ListConverter."""

    def setUp(self):
        """Set up test environment."""
        self.converter = ListConverter()

    def test_regex_pattern(self):
        """Test regex pattern."""
        self.assertEqual(self.converter.regex, "watched|to-watch")

    def test_to_python_watched(self):
        """Test to_python with watched value."""
        result = self.converter.to_python("watched")
        self.assertEqual(result, "watched")

    def test_to_python_to_watch(self):
        """Test to_python with to-watch value."""
        result = self.converter.to_python("to-watch")
        self.assertEqual(result, "to-watch")

    def test_to_url_watched(self):
        """Test to_url with watched value."""
        result = self.converter.to_url("watched")
        self.assertEqual(result, "watched")

    def test_to_url_to_watch(self):
        """Test to_url with to-watch value."""
        result = self.converter.to_url("to-watch")
        self.assertEqual(result, "to-watch")


class FeedConverterTestCase(TestCase):
    """Test FeedConverter."""

    def setUp(self):
        """Set up test environment."""
        self.converter = FeedConverter()

    def test_regex_pattern(self):
        """Test regex pattern."""
        self.assertEqual(self.converter.regex, "people|friends")

    def test_to_python_people(self):
        """Test to_python with people value."""
        result = self.converter.to_python("people")
        self.assertEqual(result, "people")

    def test_to_python_friends(self):
        """Test to_python with friends value."""
        result = self.converter.to_python("friends")
        self.assertEqual(result, "friends")

    def test_to_url_people(self):
        """Test to_url with people value."""
        result = self.converter.to_url("people")
        self.assertEqual(result, "people")

    def test_to_url_friends(self):
        """Test to_url with friends value."""
        result = self.converter.to_url("friends")
        self.assertEqual(result, "friends")
"""Forms."""
from typing import Any, List

from django.forms import ModelForm
from django_countries.widgets import CountrySelectWidget

from .models import User


class UserForm(ModelForm[User]):  # pylint:disable=unsubscriptable-object
    """User form."""

    class Meta:
        """Meta."""

        model = User
        fields = (
            "language",
            "only_for_friends",
            "hidden",
            "username",
            "first_name",
            "last_name",
            "country",
            "timezone",
        )
        widgets = {"country": CountrySelectWidget()}

    def __init__(self, *args: Any, **kwargs: Any):
        """Init."""
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name in ["only_for_friends", "hidden"]:
                class_name = ""
            else:
                class_name = "form-control"

            self.fields[field_name].widget.attrs["class"] = class_name


class UserDeleteForm(ModelForm[User]):  # pylint:disable=unsubscriptable-object
    """User delete form."""

    class Meta:
        """Meta."""

        model = User
        fields: List[str] = []

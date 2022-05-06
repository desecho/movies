from typing import Any

from django.forms import ModelForm

from .models import User


class UserForm(ModelForm[User]):  # pylint:disable=unsubscriptable-object
    class Meta:
        model = User
        fields = ("language", "only_for_friends", "username", "first_name", "last_name")

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name == "only_for_friends":
                class_name = "only-for-friends"
            else:
                class_name = "form-control"

            self.fields[field_name].widget.attrs["class"] = class_name

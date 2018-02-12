from django.forms import ModelForm

from moviesapp.models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('language', 'only_for_friends', 'username', 'first_name', 'last_name', 'location')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name == 'only_for_friends':
                class_name = 'only-for-friends'
            else:
                class_name = 'form-control'

            self.fields[field_name].widget.attrs['class'] = class_name

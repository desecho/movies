from django.core.exceptions import PermissionDenied
from django.http import Http404

from moviesapp.models import User

from .mixins import TemplateAnonymousView
from .utils import get_anothers_account, get_records


class AboutView(TemplateAnonymousView):
    template_name = 'about.html'


class GalleryView(TemplateAnonymousView):
    template_name = 'gallery.html'

    def get_context_data(self, list_name, username=None):
        if username is None and self.request.user.is_anonymous:
            raise Http404
        anothers_account = get_anothers_account(username)
        if anothers_account:
            if User.objects.get(username=username) not in self.request.user.get_users():
                raise PermissionDenied

        records = get_records(list_name, self.request.user, anothers_account)

        return {
            'records': records,
            'anothers_account': anothers_account,
            'list': list_name,
        }

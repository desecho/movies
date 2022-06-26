"""Common views."""
from django.http import HttpResponse, HttpResponseBadRequest

from ..http import AjaxAuthenticatedHttpRequest
from ..models import Record
from .mixins import AjaxView


class SaveRecordsOrderView(AjaxView):
    """
    Save records order view.

    This view is used on the list nd gallery pages.
    """

    def put(self, request: AjaxAuthenticatedHttpRequest) -> (HttpResponse | HttpResponseBadRequest):
        """Save records order."""
        try:
            records = request.PUT["records"]
        except KeyError:
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response

        for record in records:
            # If record id is not found we silently ignore it
            Record.objects.filter(pk=record["id"], user=request.user).update(order=record["order"])
        return self.success()

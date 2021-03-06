import os
import tempfile

import requests
from requests_toolbelt import MultipartEncoder

from moviesapp.models import Record

from .mixins import VkAjaxView


class UploadPosterToWallView(VkAjaxView):
    tmp_file = None

    def _get_filepath(self, record_id):
        movie = Record.objects.get(pk=record_id).movie
        file_contents = requests.get(movie.poster_big).content
        # We need to make sure that file is not deleted that is why we use `self`.
        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.tmp_file.write(file_contents)
        os.chmod(self.tmp_file.name, 0o666)  # nosec

    @staticmethod
    def _upload_file(url, filepath):
        file_ = open(filepath, 'rb')
        data = MultipartEncoder(fields={'photo': (file_.name, file_, 'image/jpg')})
        return requests.post(url, data=data, headers={'Content-Type': data.content_type}).text

    def post(self, request, **kwargs):
        try:
            record_id = int(kwargs['id'])
        except ValueError:
            return self.render_bad_request_response()
        try:
            url = request.POST['url']
        except KeyError:
            return self.render_bad_request_response()

        self._get_filepath(record_id)
        response = self._upload_file(url, self.tmp_file.name)
        return self.render_json_response({'data': response})

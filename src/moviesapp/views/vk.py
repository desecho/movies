import os
import tempfile

import requests
from requests_toolbelt import MultipartEncoder

from ..models import Record
from .mixins import VkAjaxView


class UploadPosterToWallView(VkAjaxView):
    @staticmethod
    def _get_filepath(record_id):
        movie = Record.objects.get(pk=record_id).movie
        file_contents = requests.get(movie.poster_big).content
        path = tempfile.mkstemp()[1]
        with open(path, 'w') as file_:
            file_.write(file_contents)
        path_jpg = path + '.jpg'
        os.chmod(path, 0o666)
        os.rename(path, path_jpg)
        return path_jpg

    @staticmethod
    def _upload_file(url, filepath):
        file_ = open(filepath, 'rb')
        m = MultipartEncoder(fields={'photo': (file_.name, file_, 'image/jpg')})
        return requests.post(url, data=m, headers={'Content-Type': m.content_type}).text

    def post(self, request):
        try:
            POST = request.POST
            record_id = int(POST['recordId'])
            url = POST.get('url')
        except (KeyError, ValueError):
            return self.render_bad_request_response()

        filepath = self._get_filepath(record_id)
        response = self._upload_file(url, filepath)
        return self.render_json_response({'data': response})

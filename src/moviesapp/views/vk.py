import os
import tempfile
import urllib2

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from ..models import Record
from .mixins import VkAjaxView


class UploadPosterToWallView(VkAjaxView):
    @staticmethod
    def _get_filepath(record_id):
        movie = Record.objects.get(pk=record_id).movie
        file_contents = urllib2.urlopen(movie.poster_big).read()
        path = tempfile.mkstemp()[1]
        with open(path, 'w') as file_:
            file_.write(file_contents)
        path_jpg = path + '.jpg'
        os.chmod(path, 0666)
        os.rename(path, path_jpg)
        return path_jpg

    @staticmethod
    def _upload_file(url, filepath):
        register_openers()
        datagen, headers = multipart_encode({'photo': open(filepath, 'rb')})
        request = urllib2.Request(url, datagen, headers)
        response = urllib2.urlopen(request).read()
        return response

    def post(self, request):
        try:
            POST = request.POST
            record_id = int(POST['recordId'])
            url = POST.get('url')
        except (KeyError, ValueError):
            return self.render_bad_request_response()

        filepath = self._get_filepath(record_id)
        response = self._upload_file(url, filepath)
        return self.render_json_response({'response': response})

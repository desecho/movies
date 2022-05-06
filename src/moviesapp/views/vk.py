# import os
# import tempfile

# import requests
# from django.http import HttpResponse, HttpResponseBadRequest
# from requests_toolbelt import MultipartEncoder

# from moviesapp.http import AuthenticatedHttpRequest
# from moviesapp.models import Record

# from .mixins import VkAjaxView


# class UploadPosterToWallView(VkAjaxView):
#     tmp_file = None

#     def _get_filepath(self, record_id: int) -> None:
#         movie = Record.objects.get(pk=record_id).movie
#         file_contents = requests.get(movie.poster_big).content
#         # We need to make sure that file is not deleted that is why we use `self`.
#         # TODO: remove pylint warning. Need to test this properly.
#         self.tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")  # pylint: disable=consider-using-with
#         self.tmp_file.write(file_contents)
#         os.chmod(self.tmp_file.name, 0o666)  # nosec

#     @staticmethod
#     def _upload_file(url: str, filepath: str) -> str:
#         # TODO: need to test this:
#         with open(filepath, "rb") as f:
#             data = MultipartEncoder(fields={"photo": (f.name, f, "image/jpg")})
#         return requests.post(url, data=data, headers={"Content-Type": data.content_type}).text

#     def post(self, request: AuthenticatedHttpRequest, record_id: int) -> (HttpResponse | HttpResponseBadRequest):
#         try:
#             url = request.POST["url"]
#         except KeyError:
#             return self.render_bad_request_response()

#         self._get_filepath(record_id)
#         response = self._upload_file(url, self.tmp_file.name)
#         return self.render_json_response({"data": response})

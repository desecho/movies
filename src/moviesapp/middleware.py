from django.http import QueryDict


class PutHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'PUT':
            request.PUT = QueryDict(request.body)
        response = self.get_response(request)
        return response

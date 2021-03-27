from braces.views import JsonRequestResponseMixin, LoginRequiredMixin
from django.views.generic import TemplateView as TemplateViewOriginal, View


class AjaxAnonymousView(JsonRequestResponseMixin, View):
    def success(self, **kwargs):
        response = {"status": "success"}
        response.update(kwargs)
        return self.render_json_response(response)


class AjaxView(LoginRequiredMixin, AjaxAnonymousView):
    raise_exception = True


class VkAjaxView(AjaxView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_vk_user:
            return self.no_permissions_fail(request)
        return super().dispatch(request, *args, **kwargs)


class TemplateView(LoginRequiredMixin, TemplateViewOriginal):
    pass


class TemplateAnonymousView(TemplateViewOriginal):
    pass

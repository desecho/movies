from braces.views import JsonRequestResponseMixin, LoginRequiredMixin
from django.views.generic import TemplateView as TemplateViewOriginal
from django.views.generic import View


class AjaxAnonymousView(JsonRequestResponseMixin, View):
    pass


class AjaxView(LoginRequiredMixin, AjaxAnonymousView):
    pass


class VkAjaxView(AjaxView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_vk_user:
            return self.no_permissions_fail(request)
        return super(VkAjaxView, self).dispatch(request, *args, **kwargs)


class TemplateView(LoginRequiredMixin, TemplateViewOriginal):
    pass


class TemplateAnonymousView(TemplateViewOriginal):
    pass

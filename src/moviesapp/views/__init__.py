from .mixins import TemplateAnonymousView


class AboutView(TemplateAnonymousView):
    template_name = 'about.html'

"""About view."""

from .mixins import TemplateAnonymousView


class AboutView(TemplateAnonymousView):
    """About view."""

    template_name = "about.html"

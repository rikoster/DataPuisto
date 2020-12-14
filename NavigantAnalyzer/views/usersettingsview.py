from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from NavigantAnalyzer.common import get_client_ip
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "NavigantAnalyzer/user_settings.html"
    title = "Datapuisto - Käyttäjä"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info("[{}] --------- View User {}".format(
                                     get_client_ip(self.request),
                                     self.request.user.username))
        return context

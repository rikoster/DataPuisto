from django.views.generic.detail import DetailView
from NavigantAnalyzer.models import Result
from NavigantAnalyzer.common import get_client_ip
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class ResultSettingsView(DetailView):
    model = Result
    pk_url_kwarg = 'id'
    template_name = "NavigantAnalyzer/result_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        req = self.request
        result = self.object
        logger.info("[{}] --- Display result settings {}".format(
                                    get_client_ip(req), result))
        context['title'] = f"Datapuisto - tulosasetukset - {result.id}"
        
        return context

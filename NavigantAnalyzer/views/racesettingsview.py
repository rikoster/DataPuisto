from django.views.generic.detail import DetailView
from NavigantAnalyzer.models import Race
from NavigantAnalyzer.common import get_client_ip
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class RaceSettingsView(DetailView):
    model = Race
    pk_url_kwarg = 'id'
    template_name = "NavigantAnalyzer/race_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        req = self.request
        race = self.object
        logger.info("[{}] --- Display race settings {}".format(
                                    get_client_ip(req), race))
        context['title'] = f"Datapuisto - kilpailuasetukset - {race.id}"
        
        return context

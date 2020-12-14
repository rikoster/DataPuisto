from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from NavigantAnalyzer.models import Race
from NavigantAnalyzer.common import get_client_ip
from django.utils import timezone
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class RaceUpdateView(LoginRequiredMixin, UpdateView):
    model = Race
    pk_url_kwarg = 'id'
    fields = ['url', 'raw_data_file']
    template_name = 'NavigantAnalyzer/race_form.html'
    title = "DataPuisto - päivitä kilpailu"

    def get_success_url(self):
        user = self.request.user
        logger.info("[{}] -----{} updating race {}".format(
                                     get_client_ip(self.request), 
                                     user.username, self.object))
        # handles both url and file inputs
        ext_input = self.object.get_raw_results_for_update(user)
        if ext_input:     # Download was successful
            self.object.update_raceresults_from_ext_input(ext_input)
        return reverse('race', args=[self.object.id])

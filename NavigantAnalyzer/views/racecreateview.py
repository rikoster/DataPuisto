from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from NavigantAnalyzer.forms import UploadRaceForm, UploadRaceFileForm
from NavigantAnalyzer.models import Race
from NavigantAnalyzer.common import get_client_ip
from django.utils import timezone
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class RaceCreateBaseView(LoginRequiredMixin, FormView):
    title = 'DataPuisto - kilpailun tuonti'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Load races for the list page, most recently added lowest
        endnum = min(5, Race.objects.count())
        context['races'] = Race.objects.all().order_by(
                                            '-upload_time')[:endnum]
        return context
    
    def get_success_url(self):
        return reverse('race', args=[self.object.id])


class RaceCreateFromUrlView(RaceCreateBaseView):
    form_class = UploadRaceForm
    template_name = 'NavigantAnalyzer/upload_race.html'

    def form_valid(self, form):
        req = self.request
        logger.info("[{}] --- {} uploading new race {}".format(
                                    get_client_ip(req),
                                    req.user.username,
                                    req.POST['url']))
        if form.cleaned_data['ext_input']:  # Download was successful
            self.object = Race.races.create_race(form.cleaned_data, 
                                                 req.user)
            self.object.update_raceresults_from_ext_input(
                                    form.cleaned_data['ext_input'])
        return super().form_valid(form)


class RaceCreateFromFileView(RaceCreateBaseView):
    form_class = UploadRaceFileForm
    template_name = 'NavigantAnalyzer/upload_racefile.html'

    def form_valid(self, form):
        req = self.request
        logger.info("[{}] --- {} uploading new file".format(
                                    get_client_ip(req),
                                    req.user.username))
        if form.cleaned_data['ext_input']:  # Download was successful
            self.object = Race.races.create_race(form.cleaned_data, 
                                                 req.user)
            self.object.update_raceresults_from_ext_input(
                                    form.cleaned_data['ext_input'])
        return super().form_valid(form)

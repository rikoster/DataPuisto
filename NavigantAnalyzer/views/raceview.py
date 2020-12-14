from django.views.generic.detail import DetailView
from NavigantAnalyzer.models import Race
from NavigantAnalyzer.common import get_client_ip
import logging

logger = logging.getLogger('NavigantAnalyzer.views')

class RaceView(DetailView):
    # The queryset below fastens performance, fewer
    # database hits are needed
    queryset = Race.objects.prefetch_related(
                'course_set__coursecontrols_set',
                'course_set__result_set__visit_set').all()
    pk_url_kwarg = 'id'
    template_name = "NavigantAnalyzer/race.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        req = self.request
        race = self.object
        viewmode = req.GET.get('viewmode')
        if not viewmode or viewmode == "-1":
            viewmode = "0"
        context['viewmode'] = viewmode
        logger.info("[{}] --- Display race {} in mode {}".format(
                                get_client_ip(req), race, viewmode))
        context['title'] = f"{race.serie} - {race.name}"
        return context

from django.views.generic.detail import DetailView
from NavigantAnalyzer.models import Puistoserie
from NavigantAnalyzer.common import get_client_ip
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class PuistoserieView(DetailView):
    queryset = Puistoserie.objects.prefetch_related(
                'puistoseriescore_set__puistocoursescore_set',
                'puistoseriescore_set__runner',
                'course_set__race').all()
    pk_url_kwarg = 'id'
    template_name = "NavigantAnalyzer/puistoserie_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        viewmode = self.request.GET.get('viewmode')
        if not viewmode or viewmode == "-1":
            viewmode = "0"
        context['viewmode'] = viewmode

        order_qs = self.object.puistoseriescore_set.all()
        if viewmode == "0":
            context['seriescores'] = order_qs.order_by('-score')
        else:
            context['seriescores'] = order_qs.order_by('-score_alt')

        context['courses'] = self.object.course_set.order_by('-begin')
        context['all_series'] = Puistoserie.objects.order_by('-id')[:7]
        context['title'] = f"DataPuisto - Puistosarja - {self.object.name}"
        logger.info("[{}] --------- View Puistoserie {}".format(
                                     get_client_ip(self.request), self.object))
        return context

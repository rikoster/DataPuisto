from django.views.generic.detail import DetailView
from NavigantAnalyzer.models import Result
from NavigantAnalyzer.common import get_client_ip
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class ResultView(DetailView):
    # The queryset below fastens performance, fewer
    # database hits are needed
    queryset = Result.objects.prefetch_related(
                    'visit_set__coursecontrol').all()
    pk_url_kwarg = 'id'
    template_name = "NavigantAnalyzer/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        req = self.request
        result = self.object
        viewmode = req.GET.get('viewmode')
        if not viewmode or viewmode == "-1":
            viewmode = "0"
        context['viewmode'] = viewmode
        logger.info("[{}] --- Display result {}".format(
                                    get_client_ip(req), result))
        context['title'] = f"Datapuisto tulos {result.name}"
        
        return context

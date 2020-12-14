from django.views.generic import TemplateView
from NavigantAnalyzer.models import Race, Puistoserie

class HomePageView(TemplateView):
    template_name = "NavigantAnalyzer/index.html"
    title = "DataPuisto" # layout.html uses 'title'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['races'] = \
                Race.objects.all().order_by('-begin')[:5]
        context['current_year'] = \
                Race.objects.filter(
                        begin__isnull=False).latest('begin').begin.year
        context['current_puistoserie'] = \
                Puistoserie.objects.last()
        return context

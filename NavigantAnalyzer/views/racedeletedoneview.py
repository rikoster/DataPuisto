from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class RaceDeleteDoneView(LoginRequiredMixin, TemplateView):
    template_name = "NavigantAnalyzer/delete_race_done.html"
    title = "Datapuisto - kilpailu poistettu"

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class ResultDeleteDoneView(LoginRequiredMixin, TemplateView):
    template_name = "NavigantAnalyzer/delete_result_done.html"
    title = "Datapuisto - tulos poistettu"

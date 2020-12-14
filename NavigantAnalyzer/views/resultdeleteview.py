from django.urls import reverse
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from NavigantAnalyzer.models import Result
from NavigantAnalyzer.common import get_client_ip
import logging
logger = logging.getLogger('NavigantAnalyzer.views')


class ResultDeleteView(UserPassesTestMixin, DeleteView):
    model = Result
    pk_url_kwarg = 'id'
    template_name = "NavigantAnalyzer/result_confirm_delete.html"
    title = "DataPuisto - poista tulos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info("[{}] --- Delete result {}".format(
                                    get_client_ip(self.request),
                                    self.object))
        return context

    def test_func(self):
        requester = self.request.user
        creator = self.get_object().course.race.uploaded_by
        return (requester.id == creator.id) or requester.is_superuser

    def get_success_url(self):
        logger.info("[{}] !!! ----- Delete result DONE {}".format(
                                     get_client_ip(self.request),
                                     self.kwargs.get('id')))
        return reverse('delete_result_done')

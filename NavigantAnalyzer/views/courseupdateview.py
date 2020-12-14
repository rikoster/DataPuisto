from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from NavigantAnalyzer.models import Course
from NavigantAnalyzer.common import get_client_ip
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    pk_url_kwarg = 'id'
    fields = ['puistoserie']
    template_name = 'NavigantAnalyzer/course_form.html'
    title = "DataPuisto - lisää kilpailu Puistosarjaan"

    def get_success_url(self):
        logger.info("[{}] --------- {} assigns to puistoserie {}".format(
                                     get_client_ip(self.request), 
                                     self.request.user.username,
                                     self.object))
        if self.object.puistoserie:
            # Updates several objects in puistoserie.py
            self.object.delete_self_from_puistoserie()
            self.object.puistoserie.update_puistoserie()
            return reverse('puistoserie', args=[self.object.puistoserie.id])
        else:
            self.object.delete_self_from_puistoserie()
            return reverse('race', args=[self.object.race.id])


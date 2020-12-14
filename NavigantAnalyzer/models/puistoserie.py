from django.db import models
from .puistoseriescore import Puistoseriescore
from .puistocoursescore import Puistocoursescore

class Puistoserie(models.Model):
    name = models.CharField(max_length=127)

    def __str__(self):
        return self.name

    def update_puistoserie(self):
        new_pss_objs = \
                Puistoseriescore.psss.create_or_delete_parentrelateds(self)
        Puistocoursescore.pcss.update_or_create_grandparentrelateds(
                                                    new_pss_objs, self)
        Puistoseriescore.psss.update_parentrelateds(self)

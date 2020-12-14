from django.db import models
#
# Avoid circular imports
# e.g. from .club import Club

class Runner(models.Model):
    first_name = models.CharField(max_length=63, blank=True)
    last_name = models.CharField(max_length=63, blank=True)
    name = models.CharField(max_length=127, blank=True)
    birthday = models.DateTimeField(blank=True, null=True)
    clubs = models.ManyToManyField('Club', blank=True)
    #
    def __str__(self):
        return self.first_name + " " + self.last_name + " (" + self.name + ")"

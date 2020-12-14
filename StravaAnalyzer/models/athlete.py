from django.db import models
from datetime import datetime
from .token import Token

class Athlete(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=63, null=True, blank=True)
    resource_state = models.IntegerField(null=True)
    firstname = models.CharField(max_length=63, blank=True)
    lastname = models.CharField(max_length=63, blank=True)
    city = models.CharField(max_length=63, null=True, blank=True)
    state = models.CharField(max_length=63, null=True, blank=True)
    country = models.CharField(max_length=63, null=True, blank=True)
    sex = models.CharField(max_length=1, blank=True)
    badge_type_id = models.IntegerField(null=True)
    profile_medium = models.URLField(blank=True)
    profile = models.URLField(blank=True)
    token = models.OneToOneField(Token, on_delete=models.SET_NULL, blank=True, null=True)
    activities_fetched = models.DateTimeField(default=datetime(1970, 1, 1))

    def __str__(self):
        return "Athlete - id {}, username {}, - {} {}".format(
            self.id, self.username, self.firstname, self.lastname)

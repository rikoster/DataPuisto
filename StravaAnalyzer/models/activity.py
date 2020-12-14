from django.db import models
from .athlete import Athlete
from NavigantAnalyzer.models import Runner

class Activity(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type = models.CharField(max_length=30)
    workout_type = models.IntegerField(null=True)
    name = models.CharField(max_length=200)
    distance = models.FloatField(null=True)
    moving_time = models.IntegerField(null=True)
    elapsed_time = models.IntegerField(null=True)
    total_elevation_gain = models.FloatField(null=True)
    start_latitude = models.FloatField(null=True)
    start_longitude = models.FloatField(null=True)
    end_latitude = models.FloatField(null=True)
    end_longitude = models.FloatField(null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    timezone = models.CharField(max_length=60, blank=True)
    utc_offset = models.IntegerField(null=True)
    athlete = models.ForeignKey(Athlete, on_delete=models.SET_NULL, blank=True, null=True)
    runner = models.ForeignKey(Runner, on_delete=models.SET_NULL, blank=True, null=True)
    athlete_count = models.IntegerField(null=True)
    map_id = models.CharField(max_length=30, blank=True)
    map_summary_polyline = models.CharField(max_length=400, blank=True)
    manual = models.BooleanField()
    average_speed = models.FloatField(null=True)
    max_speed = models.FloatField(null=True)
    achievement_count = models.IntegerField(null=True)
    pr_count = models.IntegerField(null=True)
    average_cadence = models.FloatField(null=True)
    average_temp = models.FloatField(null=True)
    has_heartrate = models.BooleanField()
    average_heartrate = models.FloatField(null=True)
    max_heartrate = models.FloatField(null=True)
    elev_high = models.FloatField(null=True)
    elev_low = models.FloatField(null=True)

    def __str__(self):
        return "Activity - start_date {}, id {}, type {}, name {}, distance {}, athlete {}".format(
            self.start_date, self.id, self.type, self.name, self.distance, self.athlete.username)

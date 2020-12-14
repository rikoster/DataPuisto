from django.db import models
from .athlete import Athlete
from NavigantAnalyzer.models import Runner

class ActivitySummary(models.Model):
    SUMMARY_TYPES = (
        ('A', 'Annual'),
        ('Q', 'Quarterly'),
        ('M', 'Monthly'),
        ('W', 'Weekly')
        )
    id = models.CharField(max_length=60, primary_key=True)
    summary_type = models.CharField(max_length=1, choices=SUMMARY_TYPES)
    # Total is total over all sports
    sport_type = models.CharField(max_length=30)
    athlete = models.ForeignKey(Athlete, on_delete=models.SET_NULL, blank=True, null=True)
    runner = models.ForeignKey(Runner, on_delete=models.SET_NULL, blank=True, null=True)
    dt_start = models.DateTimeField(blank=True, null=True)
    dt_end = models.DateTimeField(blank=True, null=True)
    year = models.IntegerField()
    quarter = models.IntegerField(null=True)
    month = models.IntegerField(null=True)
    week = models.IntegerField(null=True)
    activity_count = models.IntegerField()
    sum_elapsed_time = models.IntegerField()
    sum_distance = models.FloatField(null=True)
    rank_time = models.IntegerField(null=True)
    rank_distance = models.IntegerField(null=True)
    
    def __str__(self):
        return "ActivitySummary - {}".format(self.id)

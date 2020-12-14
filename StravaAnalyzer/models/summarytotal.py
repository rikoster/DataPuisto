from django.db import models

class SummaryTotal(models.Model):
    SUMMARY_TYPES = (
        ('A', 'Annual'),
        ('Q', 'Quarterly'),
        ('M', 'Monthly'),
        ('W', 'Weekly')
        )
    id = models.CharField(max_length=50, primary_key=True)
    summary_type = models.CharField(max_length=1, choices=SUMMARY_TYPES)
    # Total is total over all sports
    sport_type = models.CharField(max_length=30)
    dt_start = models.DateTimeField(blank=True, null=True)
    dt_end = models.DateTimeField(blank=True, null=True)
    year = models.IntegerField()
    quarter = models.IntegerField(null=True)
    month = models.IntegerField(null=True)
    week = models.IntegerField(null=True)
    avg_activity_count = models.FloatField()
    avg_elapsed_time = models.IntegerField()
    avg_distance = models.FloatField(null=True)

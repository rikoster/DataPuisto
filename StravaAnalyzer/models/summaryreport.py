from django.db import models

class SummaryReport(models.Model):
    SUMMARY_TYPES = (
        ('A', 'Annual'),
        ('Q', 'Quarterly'),
        ('M', 'Monthly'),
        ('W', 'Weekly')
        )
    id = models.CharField(max_length=20, primary_key=True)
    summary_type = models.CharField(max_length=1, choices=SUMMARY_TYPES)
    dt_start = models.DateTimeField(blank=True, null=True)
    dt_end = models.DateTimeField(blank=True, null=True)
    year = models.IntegerField()
    quarter = models.IntegerField(null=True)
    month = models.IntegerField(null=True)
    week = models.IntegerField(null=True)

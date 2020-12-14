from django.db import models
from .summaryreport import SummaryReport

class SummaryTable(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    report = models.ForeignKey(SummaryReport, on_delete=models.CASCADE)
    # Total is total over all sportsat
    sport_type = models.CharField(max_length=30)
    total_elapsed_time = models.IntegerField()

    class Meta:
        ordering = ['-total_elapsed_time']

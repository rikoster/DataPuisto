from django.db import models
from .summaryreport import SummaryReport

class SummaryColumn(models.Model):
    id = models.CharField(max_length=22, primary_key=True)
    report = models.ForeignKey(SummaryReport, on_delete=models.CASCADE)
    column_number = models.IntegerField()
    dt_start = models.DateTimeField(blank=True, null=True)
    dt_end = models.DateTimeField(blank=True, null=True)
    period = models.CharField(max_length=8)

    class Meta:
        ordering = ['id']

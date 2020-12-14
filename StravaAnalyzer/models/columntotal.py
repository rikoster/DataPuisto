from django.db import models
from .summarytable import SummaryTable
from .summarycolumn import SummaryColumn

class ColumnTotal(models.Model):
    id = models.CharField(max_length=42, primary_key=True)
    summarytable = models.ForeignKey(SummaryTable, on_delete=models.CASCADE)
    column = models.ForeignKey(SummaryColumn, on_delete=models.CASCADE)
    avg_activity_count = models.FloatField(null=True)
    avg_elapsed_time = models.IntegerField(null=True)
    avg_distance = models.FloatField(null=True)

    class Meta:
        ordering = ['id']

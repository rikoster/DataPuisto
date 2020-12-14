from django.db import models
from .summaryrow import SummaryRow

class SummaryCell(models.Model):
    id = models.CharField(max_length=62, primary_key=True)
    summaryrow = models.ForeignKey(SummaryRow, on_delete=models.CASCADE)
    column_number = models.IntegerField()
    dt_start = models.DateTimeField(blank=True, null=True)
    dt_end = models.DateTimeField(blank=True, null=True)
    activity_count = models.IntegerField(null=True)
    sum_elapsed_time = models.IntegerField(null=True)
    sum_distance = models.FloatField(null=True)
    rank_time = models.IntegerField(null=True)
    rank_distance = models.IntegerField(null=True)

    class Meta:
        ordering = ['id']

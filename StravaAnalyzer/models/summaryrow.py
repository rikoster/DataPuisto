from django.db import models
from .summarytable import SummaryTable
from .athlete import Athlete

class SummaryRow(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    summarytable = models.ForeignKey(SummaryTable, on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    total_activity_count = models.IntegerField()
    total_elapsed_time = models.IntegerField()
    total_distance = models.FloatField(null=True)

    class Meta:
        ordering = ['-total_elapsed_time']

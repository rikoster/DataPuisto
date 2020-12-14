from django.db import models
from django.db.models import Exists, OuterRef, Subquery

class PointsschemaManager(models.Manager):
    def get_points_subquery(self):
        return Subquery(self.filter(position=OuterRef(
                'puistoposition')).values('points'))

class Pointsschema(models.Model):
    position = models.IntegerField(primary_key=True)
    points = models.IntegerField()

    objects = models.Manager()
    schemas = PointsschemaManager()


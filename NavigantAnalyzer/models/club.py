from django.db import models

class Club(models.Model):
    name = models.CharField(max_length=63)
    
    def __str__(self):
        return self.name

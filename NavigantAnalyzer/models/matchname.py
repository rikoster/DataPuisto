from django.db import models
#
# Avoid circular imports
# from .runner import Runner

class MatchNameManager(models.Manager):

    def get_matching_runner(self, name_text):
        match = self.filter(name=name_text).first()
        if match:
            return match.runner
        else:
            return None

class MatchName(models.Model):
    runner = models.ForeignKey('Runner', on_delete=models.CASCADE)
    name = models.CharField(max_length=127)

    objects = models.Manager()
    matchnames = MatchNameManager()

    def __str__(self):
        return self.name


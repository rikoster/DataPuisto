from django.db import models
from NavigantAnalyzer.common import seconds_from_now

class Token(models.Model):
    refresh_token = models.CharField(max_length=60, primary_key=True)
    token_type = models.CharField(max_length=30)
    access_token = models.CharField(max_length=60, unique=True)
    expires_at = models.DateTimeField()
    expires_in = models.IntegerField()

    def __str__(self):
        return "Token - refresh_token {}\n access_token {}\n expires_at {}".format(
            self.refresh_token, self.access_token, self.expires_at)

    def get_strava_token(self):
        return {
            'token_type': self.token_type,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': seconds_from_now(self.expires_at)
            }

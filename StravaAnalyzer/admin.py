from django.contrib import admin
from StravaAnalyzer.models import Athlete

# Register your models here.

class AthleteAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname', 'username',
                    'activities_fetched')

admin.site.register(Athlete, AthleteAdmin)

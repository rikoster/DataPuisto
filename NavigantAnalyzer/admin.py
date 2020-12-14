from django.contrib import admin
from NavigantAnalyzer.models import Club, Runner, MatchName, Race, Puistoserie, Pointsschema

# Register your models here.

#class ClubAdmin(admin.ModelAdmin):
#    pass
admin.site.register(Club)

#class RunnerAdmin(admin.ModelAdmin):
#    pass
admin.site.register(Runner)

#class MatchNameAdmin(admin.ModelAdmin):
#    pass
admin.site.register(MatchName)

#class RaceAdmin(admin.ModelAdmin):
#    pass
admin.site.register(Race)

#class PuistoserieAdmin(admin.ModelAdmin):
#    pass
admin.site.register(Puistoserie)

#class PuistoserieAdmin(admin.ModelAdmin):
#    pass
admin.site.register(Pointsschema)

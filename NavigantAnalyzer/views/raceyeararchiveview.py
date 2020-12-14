from NavigantAnalyzer.models import Race
from django.views.generic.dates import YearArchiveView

class RaceYearArchiveView(YearArchiveView):
    title = "DataPuisto - Kilpailut"
    queryset = Race.objects.all().order_by('-begin')
    make_object_list = True
    date_field = "begin"

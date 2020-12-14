from django.views.generic.base import View
from django.core.serializers import serialize
from django.http import HttpResponse
from NavigantAnalyzer.models import Results_flat
from NavigantAnalyzer.common import get_client_ip
import logging
logger = logging.getLogger('NavigantAnalyzer.views')

class JsonFlatView(View):
    def get(self, request, raceid):
    #def get(self, request, *args, **kwargs):
        logger.info("[{}] --- Serializing race {}".format(
            get_client_ip(request), raceid))
        results = serialize('json',
                Results_flat.objects.filter(race_id=raceid))
        response = HttpResponse(results, content_type="text/json")
        response['Content-Disposition'] \
                = 'attachment; filename="results_flat_{}.json"'.format(raceid)
        return response

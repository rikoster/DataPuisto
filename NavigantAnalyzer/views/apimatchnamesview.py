import json
import logging

from django.views.generic.base import View
from django.http import HttpResponse
from NavigantAnalyzer.models import MatchName
from NavigantAnalyzer.common import get_client_ip

logger = logging.getLogger('NavigantAnalyzer.views')

class ApiMatchNamesView(View):
    def get(self, request):
    #def get(self, request, *args, **kwargs):
        logger.info("[{}] --- Serializing MatchNames".format(
                get_client_ip(request)))
        matchnames = json.dumps(
                list(MatchName.objects.values_list('name', flat=True)))
        response = HttpResponse(
                matchnames,
                content_type="application/json")
        response["Access-Control-Allow-Origin"] = '*'
        return response

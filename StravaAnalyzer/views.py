from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from StravaAnalyzer.stravasettings import AUTHORIZE_URL, CLIENT_ID, ACCESS_SCOPE
from StravaAnalyzer.fetch import update_or_create_athlete
from StravaAnalyzer.fetch import fetch_all_activities
from StravaAnalyzer.activitysummary import update_or_create_activity_summaries
from StravaAnalyzer.summaryreport import update_or_create_summaryreports
from StravaAnalyzer.models import Athlete, Activity, SummaryReport
from NavigantAnalyzer.common import get_client_ip, aware_datetime_d

import logging

logger = logging.getLogger(__name__)

# Create your views here.

def get_strava_access(request):
    # Documented here: https://developers.strava.com/docs/authentication/
    
    from urllib.parse import urlencode
    
    # These four parameters are set according to the Strava specification
    # (see the link above)
    url_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': request.build_absolute_uri(reverse('strava_access_obtained')),
        'response_type': 'code',
        'scope': ACCESS_SCOPE
        }
    url = ''.join([
        AUTHORIZE_URL,
        '?',
        urlencode(url_params)
        ])
    
    return redirect(url)

def strava_access_obtained(request):
    logger.info("[{}] --- Fetch athlete".format(get_client_ip(request)))
    code = request.GET['code']  # The code is in GET params
    athlete = update_or_create_athlete(code)
    logger.info("[{}] --- Athlete updated {}".format(
                    get_client_ip(request), athlete.username))

    return render(
        request,
        'StravaAnalyzer/athlete.html',
        {
            'title': "Datapuisto - uusi Strava-urheilija",
            'athlete': athlete
        }
        )

# This now reimplemented below, in class-based format

# def fetch_activities(request):
#    fetch_all_activities()
#    update_or_create_activity_summaries()
#    update_or_create_summaryreports()
#    return render(
#        request,
#        'StravaAnalyzer/afterfetch.html',
#        {
#            'title': "Datapuisto - Strava päivitetty",
#        }
#        )

class AthleteView(DetailView):
    model = Athlete
    template_name = "StravaAnalyzer/athlete.html"
    title = "Datapuisto - Strava perustiedot"

class SummaryReportBaseView(LoginRequiredMixin, DetailView):
    queryset = SummaryReport.objects.all()
    template_name = "StravaAnalyzer/summaryreport.html"
    title = "Datapuisto - Strava yhteenvetoraportti"

    def get_object(self):
        id_ = self.kwargs.get('id')
        logger.info("[{}] --------- SummaryReport {}".format(
                                     get_client_ip(self.request), id_))
        if id_:
            return self.queryset.get(id=id_)
        else:
            return self.queryset.latest('dt_start')

class SummaryReportAnnualView(SummaryReportBaseView):
    queryset = SummaryReport.objects.filter(summary_type='A')

class SummaryReportQuarterlyView(SummaryReportBaseView):
    queryset = SummaryReport.objects.filter(summary_type='Q')

class SummaryReportMonthlyView(SummaryReportBaseView):
    queryset = SummaryReport.objects.filter(summary_type='M')

class SummaryReportWeeklyView(SummaryReportBaseView):
    queryset = SummaryReport.objects.filter(summary_type='W')

class ActivitiesView(LoginRequiredMixin, ListView):
    model = Activity
    title = "Datapuisto - Strava aktiviteetit"
    ordering ='-start_date'
    paginate_by = 20
    paginate_orphans = 5
    allow_empty = True

    def get_queryset(self):
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        sport_type = self.request.GET.get('type')
        athlete_id = self.request.GET.get('athlete')

        q = super().get_queryset()
        if start:
            dt_start = aware_datetime_d(start)
            q = q.filter(start_date__gte=dt_start)
        if end:
            dt_end = aware_datetime_d(end)
            q = q.filter(start_date__lt=dt_end)
        if sport_type and sport_type != 'Total':
            q = q.filter(type=sport_type)
        if athlete_id:
            athlete = Athlete.objects.get(id=athlete_id)
            q = q.filter(athlete=athlete)
        return q

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        athlete_id = self.request.GET.get('athlete')
        if athlete_id:
            athlete = Athlete.objects.get(id=athlete_id)
            c['athlete_name'] = "{} {}".format(athlete.firstname, 
                                               athlete.lastname)
        return c

class FetchActivitiesView(View):
    def get(self, request):
        logger.info("[{}] --- Starting cron job check {}".format(
                get_client_ip(request),
                request.headers.get('X-Appengine-Cron'),
                ))

        # This is according to Google cloud instrctions
        if (request.headers.get('X-Appengine-Cron') and 
                get_client_ip(request) == '0.1.0.1'):

            logger.info("[{}] --- Check passed, starting cron jobs".format(
                    get_client_ip(request)))

            fetch_all_activities()
            update_or_create_activity_summaries()
            update_or_create_summaryreports()

        response = HttpResponse('[]', content_type="application/json")
        return response

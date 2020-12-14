from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
#from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.serializers import serialize
from datetime import datetime
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.dates import YearArchiveView
from django.views.generic.edit import UpdateView, DeleteView
from NavigantAnalyzer.forms import UploadRaceForm, UploadRaceFileForm
from NavigantAnalyzer.models import Race, Course, Result, Club, Runner, MatchName, Visit, Results_flat, Puistoserie
# from NavigantAnalyzer.add_init_db_values_01 import add_init_db_values
from NavigantAnalyzer.downloader import get_raw_results, get_raw_results_for_update
from NavigantAnalyzer.results_cleaner import clean_results
from NavigantAnalyzer.analyzer import get_analyzed_and_filtered_results
from NavigantAnalyzer.db_uploader import upload_results
from NavigantAnalyzer.common import get_client_ip
from NavigantAnalyzer.puistoserie import calculate_puistoserie, delete_course_from_puistoseries
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def index(request):
    # add_init_db_values()
    
    races = Race.objects.all().order_by('-begin')[:5]
    current_year = Race.objects.filter(
        begin__isnull=False).latest('begin').begin.year
    current_puistoserie = Puistoserie.objects.last()
    return render(
        request,
        "NavigantAnalyzer/index.html",
        {
            'title': "DataPuisto",
            'races': races,
            'current_year': current_year,
            'current_puistoserie': current_puistoserie
        }
    )

class RaceYearArchiveView(YearArchiveView):
    title = "DataPuisto - Kilpailut"
    queryset = Race.objects.all().order_by('-begin')
    make_object_list = True
    date_field = "begin"

#
# -------------------------------------------------------------------
#
# Race views
#
# -------------------------------------------------------------------

def race(request, raceid):
    r = get_object_or_404(Race, id=raceid)
    logger.info("[{}] --- Display race {}".format(
                                    get_client_ip(request), r))
    raceheader = "{} - {}".format(r.serie, r.name)
    viewmode = request.GET.get('viewmode')
    # -1 when nothing is selected from dropdown list
    if not viewmode or viewmode == "-1":
        viewmode = "0"
    return render(
        request,
        "NavigantAnalyzer/race.html",
        {
            'title': "Datapuisto " + raceheader,
            'race': r,
            'viewmode': viewmode
        }
    )

def race_redirect(request, raceid):
    return redirect(request.path[:-1])

def race_settings(request, raceid):
    r = get_object_or_404(Race, id=raceid)
    logger.info("[{}] --- Display race settings {}".format(
                                 get_client_ip(request), r))
    return render(request,
        'NavigantAnalyzer/race_settings.html',
        {
            'title': "DataPuisto - kilpailu",
            'race': r,
        },
    )


class RaceDeleteView(UserPassesTestMixin, DeleteView):
    model = Race
    success_url = reverse_lazy('delete_race_done')
    title = "DataPuisto - poista kilpailu"

    def get_object(self):
        id_ = self.kwargs.get('id')
        r = get_object_or_404(Race, id=id_)
        logger.info("[{}] --------- Delete race {}".format(
                                     get_client_ip(self.request), r))
        return r

    def test_func(self):
        requester = self.request.user
        creator = self.get_object().uploaded_by
        return (requester.id == creator.id) or requester.is_superuser

class RaceDeleteDoneView(LoginRequiredMixin, TemplateView):
    template_name = "NavigantAnalyzer/delete_race_done.html"
    title = "Datapuisto - kilpailu poistettu"
#
# -------------------------------------------------------------------
#
# Course views
#
# -------------------------------------------------------------------

#
# Added by Riku on 2019-11-26, part of PuistoMan additions
#
class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    pk_url_kwarg = 'id'
    fields = ['puistoserie']
    title = "DataPuisto - lisää kilpailu Puistosarjaan"

    def get_success_url(self):
        logger.info("[{}] --------- Update course {}".format(
                                     get_client_ip(self.request), 
                                     self.object))
        if self.object.puistoserie:
            # Updates several objects in puistoserie.py
            delete_course_from_puistoseries(self.object)
            calculate_puistoserie(self.object.puistoserie)
            return reverse('puistoserie', args=[self.object.puistoserie.id])
        else:
            delete_course_from_puistoseries(self.object)
            return reverse('race', args=[self.object.race.id])
#
# -------------------------------------------------------------------
#
# Result views
#
# -------------------------------------------------------------------

def result(request, resid):
    r = get_object_or_404(Result, id=resid)
    logger.info("[{}] --- Display result {}".format(
                                    get_client_ip(request), r))
    resheader = r.name
    viewmode = request.GET.get('viewmode')
    # -1 when nothing is selected from dropdown list
    if not viewmode or viewmode == "-1":
        viewmode = "0"

    return render(
        request,
        "NavigantAnalyzer/result.html",
        {
            'title': "Datapuisto tulos " + resheader,
            'result': r,
            'viewmode': viewmode
        }
    )

def result_redirect(request, resid):
    return redirect(request.path[:-1])

def result_settings(request, resid):
    r = get_object_or_404(Result, id=resid)
    logger.info("[{}] --- Display result settings {}".format(
                                 get_client_ip(request), r))
    return render(request,
        'NavigantAnalyzer/result_settings.html',
        {
            'title': "DataPuisto - tulos",
            'result' : r,
        },
    )

class ResultDeleteView(UserPassesTestMixin, DeleteView):
    model = Result
    success_url = reverse_lazy('delete_result_done')
    title = "DataPuisto - poista tulos"

    def get_object(self):
        id_ = self.kwargs.get('id')
        r = get_object_or_404(Result, id=id_)
        logger.info("[{}] --------- Delete result {}".format(
                                     get_client_ip(self.request), r))
        return r

    def test_func(self):
        requester = self.request.user
        creator = self.get_object().course.race.uploaded_by
        return (requester.id == creator.id) or requester.is_superuser

class ResultDeleteDoneView(LoginRequiredMixin, TemplateView):
    template_name = "NavigantAnalyzer/delete_result_done.html"
    title = "Datapuisto - tulos poistettu"

#
# -------------------------------------------------------------------
#
# Upload views
#
# -------------------------------------------------------------------

#
# A small change by Riku on 2020-10-08
# These are the main analysis steps when results are captured in JSON
# in raw form. This function is called from several views.
#
def upload_analysis_from_raw_JSON(results):
    clean_results(results)
    filtered = get_analyzed_and_filtered_results(results)
    return upload_results(filtered)

def send_upload_race_response(request, form, message):
    # Load races for the list page, most recently added lowest
    startnum = max(0, Race.objects.count() - 5)
    races = Race.objects.all().order_by('upload_time')[startnum:]
    return render(request,
        'NavigantAnalyzer/upload_race.html',
        {
            'title': "DataPuisto upload",
            'message': message,
            'races': races,
            'form': form
        },
    )

@login_required
def upload_race(request):
    logger.info("[{}] --- Upload race".format(get_client_ip(request)))
    if request.method == 'POST':
        form = UploadRaceForm(request.POST)
        if form.is_valid():
            logger.info("[{}] ---+++--- {} uploading url {}".format(
                                            get_client_ip(request), 
                                            request.user.username,
                                            request.POST['url']))
            results = get_raw_results(request.POST, request.user)
            if 'race' in results:     # Download was successful
                is_success = upload_analysis_from_raw_JSON(results)
                if is_success:
                    form = UploadRaceForm()
            else:
                return send_upload_race_response(request, form, 
                                                 results['status'])
    else:
        form = UploadRaceForm()
    return send_upload_race_response(request, form, "")

def send_upload_racefile_response(request, form, message):
    # Load five most recently added races for the list page
    startnum = max(0, Race.objects.count() - 5)
    races = Race.objects.all().order_by('upload_time')[startnum:]
    return render(request,
        'NavigantAnalyzer/upload_racefile.html',
        {
            'title': "DataPuisto upload",
            'message': message,
            'races': races,
            'form': form
        },
    )

@login_required
def upload_racefile(request):
    logger.info("[{}] --- Upload racefile".format(get_client_ip(request)))
    if request.method == 'POST':
        form = UploadRaceFileForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info("[{}] ---+++--- {} uploading file".format(
                        get_client_ip(request), request.user.username))
            results = get_raw_results(request.POST, request.user, f=request.FILES['file'])
            if 'race' in results:     # Download was successful
                is_success = upload_analysis_from_raw_JSON(results)
                if is_success:
                    form = UploadRaceFileForm()
            else:
                return send_upload_racefile_response(request, form,
                                                     results['status'])
    else:
        form = UploadRaceFileForm()
    return send_upload_racefile_response(request, form, "")

#
# Added by Riku on 2020-10-08, a smaller update
#
class RaceUpdateView(LoginRequiredMixin, UpdateView):
    model = Race
    pk_url_kwarg = 'id'
    fields = ['url', 'raw_data_file']
    title = "DataPuisto - päivitä kilpailu"

    def get_success_url(self):
        logger.info("[{}] --------- Update race {}".format(
                                     get_client_ip(self.request), 
                                     self.object))
        # handles both url and file inputs
        results = get_raw_results_for_update(self.object)
        if 'race' in results:     # Download was successful
            is_success = upload_analysis_from_raw_JSON(results)
        return reverse('race', args=[self.object.id])

#
# -------------------------------------------------------------------
#
# Authentication views
#
# -------------------------------------------------------------------

class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "NavigantAnalyzer/user_settings.html"
    title = "Datapuisto - Käyttäjä"

#
# -------------------------------------------------------------------
#
# Api views
#
# -------------------------------------------------------------------

def json_flat(request, raceid):
    logger.info("[{}] --- Serializing race {}".format(get_client_ip(request), raceid))
    results = serialize('json', Results_flat.objects.filter(race_id=raceid))
    response = HttpResponse(results, content_type="text/json")
    response['Content-Disposition'] \
            = 'attachment; filename="results_flat_{}.json"'.format(raceid)
    return response

#def results_flat_old(request, raceid):
#    results = Results_flat.objects.filter(race_id=raceid)
#    return render(request,
#        'NavigantAnalyzer/results_flat.html',
#        {
#            'title': "DataPuisto API results_flat",
#            'results': results
#        },
#    )
#
# -------------------------------------------------------------------
#
# Puistoserie views
#
# -------------------------------------------------------------------

class PuistoserieView(DetailView):
    model = Puistoserie
    pk_url_kwarg = 'id'
    title = "DataPuisto - Puistosarja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = self.object.course_set.order_by('-begin')
        context['all_series'] = Puistoserie.objects.order_by('-id')[:7]
        logger.info("[{}] --------- View Puistoserie {}".format(
                                     get_client_ip(self.request), self.object))
        return context

#
# ----------------------------------------------
#
# Learning material - listviews based on generic
#
# ----------------------------------------------


class ClubListView(ListView):
    model = Club

class RunnerListView(ListView):
    model = Runner

"""
Definition of urls for DataPuisto.
"""
from datetime import datetime
from django.urls import path, re_path
from django.conf.urls import include
import django.contrib.auth.views as auth_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from django.conf import settings

#import NavigantAnalyzer.views
from NavigantAnalyzer.views import HomePageView, RaceYearArchiveView,\
        RaceView, RaceSettingsView, RaceDeleteView,\
        RaceDeleteDoneView, RaceUpdateView, CourseUpdateView,\
        ResultView, ResultSettingsView, ResultDeleteView,\
        ResultDeleteDoneView, RaceCreateFromUrlView,\
        RaceCreateFromFileView, UserSettingsView, PuistoserieView,\
        JsonFlatView, ApiMatchNamesView
import StravaAnalyzer.views
from StravaAnalyzer.views import AthleteView, ActivitiesView
from StravaAnalyzer.views import SummaryReportAnnualView,\
        SummaryReportQuarterlyView, SummaryReportMonthlyView,\
        SummaryReportWeeklyView
from StravaAnalyzer.views import FetchActivitiesView

# Uncomment the next lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Modified by Riku - 2020-10-26
    path('', HomePageView.as_view(), name='index'),
    path('home', HomePageView.as_view(), name='home'),
    path('year/<int:year>', RaceYearArchiveView.as_view(),
        name='year_races'),
    path('race/<int:id>', RaceView.as_view(), name='race'),
    #url(r'^race/(\d+)$', NavigantAnalyzer.views.race, name='race'),
    path('race/<int:id>/',
        RedirectView.as_view(pattern_name='race',query_string=True),
        name='race-redirect'),
    path('race/<int:id>/settings', RaceSettingsView.as_view(),
        name='race_settings'),
    path('race/<int:id>/delete', RaceDeleteView.as_view(),
        name='delete_race'),
    path('race/delete/done', RaceDeleteDoneView.as_view(),
        name='delete_race_done'),
    path('result/<int:id>', ResultView.as_view(), name='result'),
    path('result/<int:id>/',
        RedirectView.as_view(pattern_name='result',query_string=True),
        name='result-redirect'),
    path('result/<int:id>/settings', ResultSettingsView.as_view(),
        name='result_settings'),
    path('result/<int:id>/delete', ResultDeleteView.as_view(),
        name='delete_result'),
    path('result/delete/done', ResultDeleteDoneView.as_view(),
        name='delete_result_done'),
    path('upload_race', RaceCreateFromUrlView.as_view(),
        name='upload_race'),
    path('upload_racefile', RaceCreateFromFileView.as_view(),
        name='upload_racefile'),
    path('api/matchnames', ApiMatchNamesView.as_view(),
        name='api_matchnames'),
    path('json_flat/<int:raceid>', JsonFlatView.as_view(),
        name='json_flat'),
    
    #
    # Added by Riku on 2019-11-26, PuistoMan additions
    #
    path('course/<int:id>/update', CourseUpdateView.as_view(), name='update_course'),
    path('puistoserie/<int:id>', PuistoserieView.as_view(), name='puistoserie'),

    #
    # Added by Riku on 2020-10-08, a smaller addition
    #
    path('race/<int:id>/update', RaceUpdateView.as_view(), name='update_race'),

    #
    # Added by Riku - 2019-04-18
    #
    path('athlete/<int:pk>', AthleteView.as_view(), name='athlete'),
    path('get_strava_access', StravaAnalyzer.views.get_strava_access,
        name='get_strava_access'),
    path('strava_access_obtained',
            StravaAnalyzer.views.strava_access_obtained,
            name='strava_access_obtained'),
    path('strava/annual', SummaryReportAnnualView.as_view(),
            name='summaryreport_annual'),
    path('strava/quarterly', SummaryReportQuarterlyView.as_view(),
            name='summaryreport_quarterly'),
    path('strava/monthly', SummaryReportMonthlyView.as_view(),
            name='summaryreport_monthly'),
    path('strava/weekly', SummaryReportWeeklyView.as_view(),
            name='summaryreport_weekly'),
    path('strava',
            TemplateView.as_view(template_name='StravaAnalyzer/strava_views.html'),
            name='strava_views'),
    path('activities', ActivitiesView.as_view(), name='activities'),
    path('fetchactivities', FetchActivitiesView.as_view(),
            name='fetchactivities'),

    path('login/',
            auth_views.LoginView.as_view(template_name='NavigantAnalyzer/login.html'),
            name='login'),
    path('logout',
        auth_views.LogoutView.as_view(next_page='/'),
        name='logout'),
    path('user_settings', UserSettingsView.as_view(), name='user_settings'),
    path('password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='NavigantAnalyzer/password_change_form.html'
        ),
        name='password_change'),
    path('password_change/done',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='NavigantAnalyzer/password_change_done.html'
        ),
        name='password_change_done'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    path('admin/', admin.site.urls),
]

# Don't use in production
if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

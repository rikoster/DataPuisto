from django.db import models
from django.contrib.auth.models import User
#
# Avoid circular imports, none here
from .course import Course
from NavigantAnalyzer.downloaders import download_from_ext_input
from NavigantAnalyzer.analyzers import clean_results,\
        get_analyzed_and_filtered_results
from django.utils import timezone
from datetime import datetime
from NavigantAnalyzer.common import aware_datetime, datetime_string


class RaceManager(models.Manager):

    def create_race(self, form_data, user):
        ext_input = form_data['ext_input']
        url = form_data['url'] if 'url' in form_data else ""
        f = form_data['file'] if 'file' in form_data else None
        
        r = self.model(
            name=ext_input['name'],
            url=url,
            serie=ext_input['serie'],
            begin=aware_datetime(ext_input['begin']),
            raw_data_file=f,
            upload_time=timezone.now(),
            uploaded_by=user
            )
        if 'uuid' in ext_input and ext_input['uuid']:
            r.opt_uuid = ext_input['uuid']
        r.save()
        return r
    
    def can_be_added(self, ext_input):
        input_begin = aware_datetime(ext_input['begin'])
        n = self.filter(name=ext_input['name'], 
                        serie=ext_input['serie'], 
                        begin=input_begin).count()
        return n == 0


class Race(models.Model):
    name = models.CharField(max_length=127)
    url = models.URLField(blank=True)
    opt_uuid = models.UUIDField(blank=True, null=True)
    serie = models.CharField(max_length=127, blank=True)
    begin = models.DateTimeField(blank=True, null=True)
    raw_data_file = models.FileField(upload_to='races/%Y', blank=True)
    upload_time = models.DateTimeField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    objects = models.Manager()
    races = RaceManager()
        
    @property
    def begin_string(self):
        # return self.begin.strftime("%c")
        # return self.begin.strftime("%Y-%m-%d %H:%M")
        return datetime_string(self.begin)

    @property
    def month(self):
        return timezone.make_aware(datetime(self.begin.year,
                    self.begin.month, 1, 0, 0, 0))

    def __str__(self):
        return "{} ({} {})".format(self.name, self.serie, self.begin_string)

    def get_absolute_url(self):
        return "/race/{}".format(self.id)

    def get_api_url(self):
        return "/json_flat/{}".format(self.id)

    def get_raw_results_for_update(self, user):
        ext_input = download_from_ext_input(self.url,
                                self.raw_data_file)
        if ext_input:
            self.name = ext_input['name']
            self.serie = ext_input['serie']
            self.begin = aware_datetime(ext_input['begin'])
            self.uploaded_by = user
            self.upload_time = timezone.now()
            if 'uuid' in ext_input and ext_input['uuid']:
                self.opt_uuid = ext_input['uuid']
            self.save()
        return ext_input

    def update_raceresults_from_ext_input(self, ext_input):

        clean_results(ext_input)
        club_results = get_analyzed_and_filtered_results(ext_input)

        Course.courses.update_or_create_parentrelateds(
                    club_results['results'], self)
        

from django.db import models
from django.db.models import F
#
# Avoid circular imports
# from .course import Course
# from .runner import Runner
from .visit import Visit
from .matchname import MatchName
from .dpbasemanager import DPBaseManager
from NavigantAnalyzer.common import aware_datetime
from NavigantAnalyzer.analyzers import status_manual, LONGTIME

#LONGTIME = 28800

class ResultManager(DPBaseManager):
    matchattr = 'name'
    update_fields_to_exclude = ['id', 'course']
    is_bulk_create = False

    def get_parentqueryset(self, course):
        return self.filter(course=course)

    def get_initialized_obj(self, res_dict, course):
        return self.model(course=course,
                          name=res_dict['name'],
                          status="") # Initial, will be changed

    def launch_u_or_c_for_relatedsets(self, res_dict_list, cc_list):
        # We loop the res_dict_list for the second time (the first time
        # was in the BaseManager's 'prep_parentrelateds') to launch the
        # 'update_or_create's for the visits of the result. The correct
        # result object is stored res_dict['obj'].
        for res_dict in res_dict_list:
            if 'controltimes' in res_dict \
                    and not status_manual(res_dict):
                Visit.visits.update_or_create_parentrelateds(
                    res_dict['controltimes'], res_dict['obj'], cc_list)


class Result(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    runner = models.ForeignKey('Runner', on_delete=models.SET_NULL, blank=True, null=True)
    emit = models.CharField(max_length=12, blank=True, null=True)
    club = models.CharField(max_length=63, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    read_time = models.DateTimeField(blank=True, null=True)
    # Modified by Riku 2020-04-26 NaviSport API change modification
    # Status info is much easier to grasp in text code vs. integer.
    # Integer was the original format.
    # status = models.IntegerField(blank=True)
    status = models.CharField(max_length=12, blank=True)
    time = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    puistoposition = models.IntegerField(blank=True, null=True)
    # Added by Riku 2019-11-27 PuistoMan additions
    puistodiff_time_l = models.IntegerField(null=True)
    puistodiff_time_pm = models.IntegerField(null=True)
    puistoperc_time_l = models.FloatField(null=True)
    puistoperc_time_pm = models.FloatField(null=True)
    # Percentage, result's max level vs. PuistoMan
    puisto_max_level = models.FloatField(null=True) 
    # Percentage: puistoperc_time_pm / puisto_max_level
    puisto_success = models.FloatField(null=True)
    # Time, calculated using best legs or puisto_max_level * puistoman
    puisto_optimum = models.IntegerField(null=True)
    # Time: time - puisto_optimum
    puisto_mistakes = models.IntegerField(null=True)

    objects = models.Manager()
    results = ResultManager()

    class Meta:
        ordering = [F('position').asc(nulls_last=True)]
    
    def __str__(self):
        return "{} - {}".format(self.name, str(self.course))

    def get_absolute_url(self):
        return "/result/{}".format(self.id)

    def match_obj_fields_to_dict(self, res_dict, *args):
        # *args are in the function signature, the dpbasemanager call to
        # to this function carries the cc_list, but it is not used here

        self.runner = MatchName.matchnames.get_matching_runner(
                        res_dict['name']) # None if no match
        if res_dict['starttime']:
            self.start_time = aware_datetime(res_dict['starttime'])
        else:
            self.start_time = None
        if res_dict['readtime']:
            self.read_time = aware_datetime(res_dict['readtime'])
        else:
            self.read_time = None

        for key, value in res_dict.items():
            if hasattr(self, key) and key not in ['id', 'start_time',
                                                'read_time', 'course']:
                setattr(self, key, value)
        # Added by Riku on 2020-10-09
        if self.time == LONGTIME:
            self.time = None

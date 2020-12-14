from django.db import models
#
# Avoid circular imports
# from .course import Course
from .dpbasemanager import DPBaseManager

class CoursecontrolsManager(DPBaseManager):
    matchattr = 'ordernumber'
    update_fields_to_exclude = ['id', 'course']
    is_bulk_create = False

    def get_parentqueryset(self, course):
        return self.filter(course=course)

    def get_initialized_obj(self, cc_dict, course):
        return self.model(course=course,
                          ordernumber=cc_dict['ordernumber'],
                          code=cc_dict['code'])

    def launch_u_or_c_for_relatedsets(self, cc_dict_list):
        pass

class Coursecontrols(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    ordernumber = models.IntegerField()
    code = models.IntegerField()
    mean_time = models.IntegerField(blank=True, null=True)
    min_time = models.IntegerField(blank=True, null=True)
    mean_puistotime = models.IntegerField(blank=True, null=True)
    min_puistotime = models.IntegerField(blank=True, null=True)
    leg_mean_time = models.IntegerField(blank=True, null=True)
    leg_min_time = models.IntegerField(blank=True, null=True)
    leg_mean_puistotime = models.IntegerField(blank=True, null=True)
    leg_min_puistotime = models.IntegerField(blank=True, null=True)
    # Added by Riku 2019-11-27 PuistoMan addition
    puistoman_time = models.IntegerField(null=True)
    # Added by Riku 2020-04-26 NaviSport API change addition
    distance = models.IntegerField(null=True)

    objects = models.Manager()
    ccs = CoursecontrolsManager()
    
    def __str__(self):
        return "{} code: {} - {}".format(self.ordernumber, self.code, self.course)

    def match_obj_fields_to_dict(self, cc_dict):
        for key, value in cc_dict.items():
            if hasattr(self, key) and key not in ['id', 'course']:
                setattr(self, key, value)

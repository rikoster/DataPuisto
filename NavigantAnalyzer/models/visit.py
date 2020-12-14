from django.db import models
#
# Avoid circular imports
# from .result import Result
# from .coursecontrols import Coursecontrols
from .dpbasemanager import DPBaseManager
from NavigantAnalyzer.analyzers import LONGTIME

#LONGTIME = 28800

class VisitManager(DPBaseManager):
    matchattr = 'ordernumber'
    update_fields_to_exclude = ['id', 'result']
    is_bulk_create = True

    def get_parentqueryset(self, result):
        return self.filter(result=result)

    def get_initialized_obj(self, visit_dict, result):
        return self.model(result=result,
                          ordernumber=visit_dict['ordernumber'],
                          code=visit_dict['code']) 

    def launch_u_or_c_for_relatedsets(self, visit_dict_list, *args):
        pass


class Visit(models.Model):
    result = models.ForeignKey('Result', on_delete=models.CASCADE)
    coursecontrol = models.ForeignKey('Coursecontrols', on_delete=models.SET_NULL, null=True)
    ordernumber = models.IntegerField()
    code = models.IntegerField()
    time = models.IntegerField(null=True)
    position = models.IntegerField(blank=True, null=True)
    puistoposition = models.IntegerField(blank=True, null=True)
    leg_time = models.IntegerField(blank=True, null=True)
    leg_position = models.IntegerField(blank=True, null=True)
    leg_puistoposition = models.IntegerField(blank=True, null=True)
    # Added by Riku 2019-11-27 PuistoMan additions
    puistodiff_time_l = models.IntegerField(null=True)
    puistodiff_time_pm = models.IntegerField(null=True)
    leg_puistodiff_time_l = models.IntegerField(null=True)
    leg_puistodiff_time_pm = models.IntegerField(null=True)
    leg_puistoperc_time_l = models.FloatField(null=True)
    leg_puistoperc_time_pm = models.FloatField(null=True)
    # Percentage: leg_min_puistotime / (result.puisto_max_level * leg_time)
    puisto_success = models.FloatField(null=True)

    objects = models.Manager()
    visits = VisitManager()

    
    def __str__(self):
        return "Visit {} code: {} - {}".format(self.ordernumber, self.code, self.result)

    def match_obj_fields_to_dict(self, visit_dict, cc_list=[]):
        cc = next(ctrl for ctrl in cc_list
                  if ctrl.ordernumber == self.ordernumber)
        self.coursecontrol = cc
        if visit_dict['time'] and visit_dict['time'] < LONGTIME:
            for key, value in visit_dict.items():
                if hasattr(self, key) and \
                        key not in ['id', 'result', 'coursecontrol']:
                    setattr(self, key, value)

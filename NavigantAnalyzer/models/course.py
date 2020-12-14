from django.db import models
#
# Avoid circular imports
# from .race import Race
# from .puistoserie import Puistoserie
from .coursecontrols import Coursecontrols
from .result import Result
from .dpbasemanager import DPBaseManager
from NavigantAnalyzer.common import aware_datetime


class CourseManager(DPBaseManager):
    matchattr = 'name'
    update_fields_to_exclude = ['id', 'race', 'puistoserie']
    is_bulk_create = False

    def get_parentqueryset(self, race):
        return self.filter(race=race)

    def get_initialized_obj(self, course_dict, race):
        return self.model(race=race,
                          name=course_dict['name'])

    def launch_u_or_c_for_relatedsets(self, course_dict_list):

        # We loop the course_dict_list for the second time (the first time
        # was in the BaseManager's 'prep_parentrelateds') to launch the
        # 'update_or_create's for the visits of the result. The correct
        # course object is stored course_dict['obj'].
        for course_dict in course_dict_list:

            cc_list = Coursecontrols.ccs.update_or_create_parentrelateds(
                    course_dict['controls'], course_dict['obj'])

            Result.results.update_or_create_parentrelateds(
                    course_dict['results'], course_dict['obj'], cc_list)


class Course(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE)
    begin = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=63)
    # Comment by Riku 2020-04-26 - now in NaviSport API this field is
    # 'distance', not 'length'. But for now preserving the old name.
    length = models.IntegerField(blank=True, null=True)
    num_participants = models.IntegerField(blank=True, null=True)
    mean_time = models.IntegerField(blank=True, null=True)
    min_time = models.IntegerField(blank=True, null=True)
    mean_puistotime = models.IntegerField(blank=True, null=True)
    min_puistotime = models.IntegerField(blank=True, null=True)
    # Added by Riku 2019-11-27 PuistoMan additions
    puistoman_time = models.IntegerField(null=True)
    puistoserie = models.ForeignKey('Puistoserie', on_delete=models.SET_NULL, null=True)

    objects = models.Manager()
    courses = CourseManager()

    def __str__(self):
        return "{} - {}".format(self.name, self.race)

    def match_obj_fields_to_dict(self, course_dict):
        self.begin = aware_datetime(course_dict['begin'])

        for key, value in course_dict.items():
            if hasattr(self, key) and key not in ['id', 'race', 'begin']:
                setattr(self, key, value)

    def delete_self_from_puistoserie(self):
        pcc_objs = self.puistocoursescore_set.all()
        if pcc_objs:
            puistoserie = pcc_objs.first().puistoseriescore.puistoserie
            pcc_objs.delete()
            puistoserie.update_puistoserie()


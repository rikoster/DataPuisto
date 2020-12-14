from django.db import models
from django.db.models import Q, Count, Subquery, OuterRef
#
# Avoid circular imports
# from .course import Course
# from .puistoseriescore import Puistoseriescore

from .result import Result
from .pointsschema import Pointsschema
from .dpbasemanager import DPBaseManager

class PuistocoursescoreManager(DPBaseManager):

    def update_or_create_grandparentrelateds(self,
                                        new_pss_objs, puistoserie):
        # No need to remove obsolete objs here, they have been all
        # removed in update_or_create_parentrelateds for pss.
        #
        # The course needs to be checked before creating runnerrelateds
        c = self.get_new_course(puistoserie)
        self.create_new_runnerrelateds(new_pss_objs, puistoserie)
        if c:
            self.create_new_courserelateds(c, puistoserie, new_pss_objs)
        self.update_curr_grandparentrelateds(puistoserie)

    def create_new_runnerrelateds(self, new_pss_objs, puistoserie):
        # For the runner(s) in puistoserie without any prior
        # Puistocoursescore entries...
        # We want to have a Puistoseriescore object for every cell in
        # the table, not just the ones with a score based on a result.
        new_objs = [self.model(puistoseriescore=pss_obj,
                               course=course,
                               begin=course.begin)
                    for pss_obj in new_pss_objs 
                    for course in puistoserie.course_set.all()] 
        if new_objs:
            self.bulk_create(new_objs)

    def create_new_courserelateds(self, course, puistoserie, new_pss_objs):
        # For the course(s) in puistoserie without any prior
        # Puistocoursescore entries...
        # We want to have a Puistocoursescore object for every cell in
        # the table, not just the ones with a score based on a result.
        # We exclude the new_pss_objs, for those the puistocoursescore
        # objects have already been created, even for the new course.
        
        new_pss_obj_ids = set(obj.id for obj in new_pss_objs)
        old_pss_obj_qs = puistoserie.puistoseriescore_set.filter(
                ~Q(id__in=new_pss_obj_ids))

        new_objs = [self.model(course=course,
                               begin=course.begin,
                               puistoseriescore=pss_obj)
                    for pss_obj in old_pss_obj_qs]
        if new_objs:
            self.bulk_create(new_objs)

    def update_curr_grandparentrelateds(self, puistoserie):
        # All the Puistocoursescore objects for a puistoserie
        curr_objs = self.get_curr_queryset(puistoserie)
        if curr_objs:
            for curr_obj in curr_objs:
                curr_obj.score = curr_obj.calc

            self.bulk_update(curr_objs, ['score'])
    #
    # ***************************************************************
    #

    def get_new_course(self, puistoserie):
        # Get course(s) in puistoserie without any Puistocoursescore
        # entries
        return puistoserie.course_set.all(
                        ).annotate(
                                  num_pcs=Count('puistocoursescore')
                                  ).filter(
                                          num_pcs=0).first()

    def get_score_subquery(self):
        return Subquery(Result.objects.filter(
                course=OuterRef('course'),
                runner=OuterRef('puistoseriescore__runner')
                ).annotate(
                          score=Pointsschema.schemas.get_points_subquery()
                          ).values('score'))

    def get_curr_queryset(self, puistoserie):
        return self.filter(
                          puistoseriescore__puistoserie=puistoserie
                          ).annotate(
                                    calc=self.get_score_subquery()
                                    )

#
# *******************************************************************
#
class Puistocoursescore(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    puistoseriescore = models.ForeignKey('Puistoseriescore', on_delete=models.CASCADE)
    begin = models.DateTimeField(blank=True, null=True)
    score = models.IntegerField(null=True)

    objects = models.Manager()
    pcss = PuistocoursescoreManager()

    class Meta:
        ordering = ['-begin']

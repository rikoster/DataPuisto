from django.db import models
from django.db.models import Sum, Min, Exists, OuterRef, Subquery
from django.db.models.functions import Coalesce
#
# Avoid circular imports
# from .puistoserie import Puistoserie
# from .runner import Runner

from .result import Result
from .puistocoursescore import Puistocoursescore
from .pointsschema import Pointsschema
from .dpbasemanager import DPBaseManager

class PuistoseriescoreManager(DPBaseManager):

    def create_or_delete_parentrelateds(self, puistoserie):
        self.remove_obsolete_parentrelateds(puistoserie)
        # The new_objs list is returned, it will used in the creation
        # of the new Puistocoursescore objects.
        new_objs = self.create_new_parentrelateds(puistoserie)
        return new_objs

    def remove_obsolete_parentrelateds(self, puistoserie):
        # It is possible that a race and its course is moved to another
        # puistoserie (there may have been a mistake). It may be that
        # some runners have no more races in the puistoserie, and they
        # become obsolete.
        obsolete_id_set = self.get_obsolete_id_set(puistoserie)
        if obsolete_id_set:
            self.filter(id__in=obsolete_id_set).delete()

    def create_new_parentrelateds(self, puistoserie):
        # New races (and their courses) may bring new runners, not yet
        # in the Puistoseriescore objects of the puistoserie.
        # We have to use loose queryset in order to get runner objects,
        # not just runner ids in the result.
        qs_objs = self.get_new_queryset(puistoserie)
        new_objs = list()
        runner_ids = set()
        for obj in qs_objs:
            if obj.runner.id not in runner_ids:
                # Not bulk-creating, creating here
                new_objs.append(self.create(puistoserie=puistoserie,
                                            runner=obj.runner))
                runner_ids.add(obj.runner.id)
        return new_objs

    def update_parentrelateds(self, puistoserie):
        curr_objs = self.get_score_queryset(puistoserie)
        # Used in obtaining position.
        score_list = [obj.calc for obj in curr_objs]
        score_list.sort(reverse=True)
        # This is the total score without the weakest score
        score_list_alt = [obj.calc - obj.calcmin for obj in curr_objs]
        score_list_alt.sort(reverse=True)
        for obj in curr_objs:
            obj.score = obj.calc
            obj.score_alt = obj.calc - obj.calcmin
            obj.position = score_list.index(obj.score) + 1
            obj.position_alt = score_list_alt.index(obj.score_alt) + 1
        if curr_objs:
            self.bulk_update(
                    curr_objs,
                    ['score', 'score_alt', 'position', 'position_alt'])

    #
    # ***************************************************************
    #
    def get_exists_result_subquery(self):
        return Exists(Result.objects.filter(
                            course__puistoserie=OuterRef('puistoserie'),
                            runner=OuterRef('runner')))

    def get_obsolete_id_set(self, puistoserie):
        return set(self.filter(~self.get_exists_result_subquery(),
                               puistoserie=puistoserie
                               ).values_list('id', flat=True))

    def get_exists_puistoseriescore_subquery(self):
        # Has to test both runner and puistoserie
        return Exists(self.filter(
                        runner=OuterRef('runner'), 
                        puistoserie=OuterRef('course__puistoserie')))

    def get_new_queryset(self, puistoserie):
        # We have to use loose queryset in order to get Runner objects,
        # not just runner ids in the result.
        return Result.objects.filter(
                ~self.get_exists_puistoseriescore_subquery(),
                course__puistoserie=puistoserie
                )

    def get_score_subquery(self):
        # We use the django notation here to first get the score for all
        # courses per runner, and then grouping by runner to get 
        # the sum, the total score for a runner.
        return Subquery(Result.objects.filter(
                course__puistoserie=OuterRef('puistoserie'),
                runner=OuterRef('runner')
                        ).annotate(
                        score=Pointsschema.schemas.get_points_subquery()
                        ).values('runner').annotate(
                                score=Sum(Coalesce('score', 0))
                                ).values('score'))

    def get_minscore_subquery(self):
        return Subquery(Puistocoursescore.objects.filter(
                puistoseriescore=OuterRef('id')
                        ).values('puistoseriescore'
                        ).annotate(
                        calcmin=Min(Coalesce('score', 0))
                        ).values('calcmin'))

    def get_score_queryset(self, puistoserie):
        # We want to return only non-obsolete pss objects
        # so that obsolete ones can be deleted.
        return self.filter(puistoserie=puistoserie
                           ).annotate(
                                     calc=self.get_score_subquery(),
                                     calcmin=self.get_minscore_subquery())
#
# *******************************************************************
#
class Puistoseriescore(models.Model):
    puistoserie = models.ForeignKey('Puistoserie', on_delete=models.CASCADE)
    runner = models.ForeignKey('Runner', on_delete=models.SET_NULL, null=True)
    score = models.IntegerField(null=True)
    score_alt = models.IntegerField(null=True) # Added on 2020-11-17 by Riku
    position = models.IntegerField(null=True)
    position_alt = models.IntegerField(null=True) # Added on 2020-11-17

    objects = models.Manager()
    psss = PuistoseriescoreManager()

    # class Meta:
    #     ordering = ['-score']

from NavigantAnalyzer.models.runner import Runner
from NavigantAnalyzer.models.puistoseriescore import Puistoseriescore
from NavigantAnalyzer.models.puistocoursescore import Puistocoursescore
from NavigantAnalyzer.models.pointsschema import Pointsschema

from django.db.models import Sum

def calculate_puistoserie(puistoserie):
    calculate_scores(puistoserie)
    # Added by Riku on 2020-10-18
    calculate_positions(puistoserie)
#
# **********************************************
#
def calculate_scores(puistoserie):
    course_list = list(puistoserie.course_set.all())
    for runner in get_all_puistoserie_runners(puistoserie):
        pss, created = Puistoseriescore.objects.get_or_create(
            puistoserie=puistoserie, 
            runner=runner,
            defaults={'score': None, 'position': None}
            )
        for course in course_list:
            temp = Puistocoursescore.objects.update_or_create(
                puistoseriescore=pss,
                course=course,
                defaults={
                    'begin': course.race.begin,
                    'score': get_puistoscore(course, runner)
                    }
                )
        pss.score = get_puistoseriescore(pss)
        pss.save()

# Added by Riku on 2020-10-18 when position field was added
def calculate_positions(puistoserie):
    # This function relies on the defined ordering of Puistoseriescores
    pss_qs = puistoserie.puistoseriescore_set.all()
    score_list = [pss_obj.score for pss_obj in pss_qs]
    for pss_obj in pss_qs:
        # list.index gives the first occurrence in the list
        pss_obj.position = score_list.index(pss_obj.score) + 1
        pss_obj.save()  

def get_all_puistoserie_runners(puistoserie):
    runner_qs = Runner.objects.raw('''
    SELECT
    runner.id
    FROM
    NavigantAnalyzer_puistoserie as puistoserie,
    NavigantAnalyzer_course as course,
    NavigantAnalyzer_result as result,
    NavigantAnalyzer_runner as runner
    WHERE
    course.puistoserie_id=puistoserie.id AND
    result.course_id=course.id AND
    result.runner_id=runner.id AND
    puistoserie.id={}
    '''.format(puistoserie.id))
    #
    return runner_qs

def get_puistoscore(course, runner):
    if course.result_set.filter(runner=runner).exists():
        position = course.result_set.get(runner=runner).puistoposition
        #
        # Riku added on 2020-05-22 - previously also rejected got points
        # Now fixing this error.
        if position: # Not None
            return Pointsschema.objects.get(position=position).points
        else:
            return None
    else:
        return None

def get_puistoseriescore(pss_obj):
    if pss_obj.puistocoursescore_set.exists():
        aggr_dict = pss_obj.puistocoursescore_set.aggregate(Sum('score'))
        return aggr_dict['score__sum']
    else:
        return None

def delete_course_from_puistoseries(course_obj):
    puistoserie = delete_puistocoursescores_per_course(course_obj)
    # continue only if there were some puistocoursescores to delete
    if puistoserie:
        # Update puistoseriescores
        for pss in puistoserie.puistoseriescore_set.all():
            pss.score = get_puistoseriescore(pss)
            if pss.score is None:  # No actual scores for this runner
                pss.delete()
            else:
                pss.save()

def delete_puistocoursescores_per_course(course_obj):
    delete_qs = Puistocoursescore.objects.raw('''
        SELECT
        puistocoursescore.id
        FROM
        NavigantAnalyzer_puistoserie as puistoserie,
        NavigantAnalyzer_puistoseriescore as puistoseriescore,
        NavigantAnalyzer_puistocoursescore as puistocoursescore,
        NavigantAnalyzer_course as course
        WHERE
        puistoseriescore.puistoserie_id=puistoserie.id AND
        puistocoursescore.puistoseriescore_id=puistoseriescore.id AND
        puistocoursescore.course_id=course.id AND
        course.id={}
    '''.format(course_obj.id))
    if len(delete_qs) > 0:
        puistoserie = delete_qs[0].puistoseriescore.puistoserie
        for pcs in delete_qs:
            pcs.delete()
        return puistoserie
    else:
        return None


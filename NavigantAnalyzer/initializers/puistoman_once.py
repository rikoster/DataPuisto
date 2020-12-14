from django.db.models import Sum

from NavigantAnalyzer.models import Course, Coursecontrols, Result, Visit

import logging

logger = logging.getLogger(__name__)

#
# The module added by Riku on 2019-11-28 to calculate once the new PuistoMan
# fields added on November 2019 to existing data.
#

# Old version, part of planning phase on 2019-11-28 [by Riku]
# was used in multiple functions of this module

#ALL_visits_qs = Visit.objects.raw('''
#    SELECT
#    visit.*,
#    coursecontrols.id,
#    coursecontrols.min_puistotime,
#    coursecontrols.leg_min_puistotime,
#    coursecontrols.puistoman_time
#    FROM
#    NavigantAnalyzer_course as course,
#    NavigantAnalyzer_coursecontrols as coursecontrols,
#    NavigantAnalyzer_result as result,
#    NavigantAnalyzer_visit as visit
#    WHERE
#    coursecontrols.course_id=course.id AND
#    result.course_id=course.id AND
#    visit.result_id=result.id AND
#    visit.ordernumber = coursecontrols.ordernumber
#''')

def for_all_obj_do_puistoman_updates():
    logger.info("=== --- Start of PuistoMan updates")
    for_all_obj_update_puistoman_course_fields()
    logger.info("=== --- Course PuistoMan updates done")
    for_all_obj_update_puistoman_coursecontrols_fields()
    logger.info("=== --- Coursecontrol PuistoMan updates done")
    for_all_obj_update_puistoman_visit_cc_fields()
    logger.info("=== --- Visit CC updates done")
    for_all_obj_update_puistoman_result_fields_1()
    logger.info("=== --- Result PuistoMan updates 1 done")
    for_all_obj_update_puistoman_visit_fields_rest()
    logger.info("=== --- Visit PuistoMan updates done - the rest")
    for_all_obj_update_puistoman_result_fields_2()
    logger.info("=== --- All PuistoMan updates done")

def for_all_obj_update_puistoman_course_fields():
    all_courses_qs = Course.objects.annotate(
        puistoman_time_calc=Sum('coursecontrols__leg_min_puistotime'))
    for course in all_courses_qs:
        course.puistoman_time = course.puistoman_time_calc
        course.begin = course.race.begin
        course.save()

def for_all_obj_update_puistoman_coursecontrols_fields():
    # Ensure that coursecontrols objects are in right order
    all_controls_qs = Coursecontrols.objects.order_by(
        'course_id', 'ordernumber')
    course = -1
    for control in all_controls_qs:
        # calculate new stats only when old stats exist for the course
        if control.course.min_puistotime:
            if control.course_id != course:
                puistoman_time = 0
                course = control.course_id
            puistoman_time += control.leg_min_puistotime
            control.puistoman_time = puistoman_time
            control.save()

def for_all_obj_update_puistoman_visit_cc_fields():
    all_visits_qs = Visit.objects.raw('''
        SELECT
        visit.*,
        coursecontrols.id as cc_id
        FROM
        NavigantAnalyzer_course as course,
        NavigantAnalyzer_coursecontrols as coursecontrols,
        NavigantAnalyzer_result as result,
        NavigantAnalyzer_visit as visit
        WHERE
        coursecontrols.course_id=course.id AND
        result.course_id=course.id AND
        visit.result_id=result.id AND
        visit.ordernumber = coursecontrols.ordernumber
    ''')
    for v in all_visits_qs:
        cc = Coursecontrols.objects.get(id=v.cc_id)
        v.coursecontrol = cc
        v.save()

def for_all_obj_update_puistoman_result_fields_1():
    for result in Result.objects.all():
        update_puistoman_result_fields_1(result)
        logger.info("--- {} --- Result update 1 done".format(
            result.id))

def for_all_obj_update_puistoman_visit_fields_rest():
    result_id = -1
    prev_visit = None

    # Visits are ordered by id, crucial for this function
    for visit in Visit.objects.all():
        if visit.result.id != result_id:
            comp_time = visit.coursecontrol.leg_min_puistotime
            logger.info("--- {} --- Visits update done".format(
                result_id))
            result_id = visit.result.id
        else:
            comp_time = visit.coursecontrol.min_puistotime \
                - prev_visit.coursecontrol.min_puistotime
        prev_visit = visit

        update_puistoman_visit_fields_rest(visit, comp_time)

def for_all_obj_update_puistoman_result_fields_2():
    for result in Result.objects.all():
        update_puistoman_result_fields_2(result)
        logger.info("--- {} --- Result update 2 done".format(
            result.id))

def update_puistoman_result_fields_1(r):
    if r.status == 0:   # A valid result
        r.puistodiff_time_pm = r.time - r.course.puistoman_time
        r.puistodiff_time_l = r.time - r.course.min_puistotime
        r.puistoperc_time_pm = r.course.puistoman_time / r.time
        r.puistoperc_time_l = r.course.min_puistotime / r.time

        # using filter returns an new QuerySet
        # visits_qs = ALL_visits_qs.filter(result_id=r.id)
        visits_qs = Visit.objects.filter(result_id=r.id)
        visits = list(visits_qs)
        # calculate_puisto_max_level-function in analyzer.py -module
        r.puisto_max_level = calculate_puisto_max_level_obj(visits)

        r.puisto_success = r.puistoperc_time_pm / r.puisto_max_level
    
        r.save()

def update_puistoman_visit_fields_rest(v, comp_time):
    if v.leg_time > 0:   # A valid visit record
        cc = v.coursecontrol
        v.puistodiff_time_l = v.time - cc.min_puistotime
        v.puistodiff_time_pm = v.time - cc.puistoman_time
        v.leg_puistodiff_time_pm = v.leg_time - cc.leg_min_puistotime
        v.leg_puistodiff_time_l = v.leg_time - comp_time
        v.leg_puistoperc_time_pm = cc.leg_min_puistotime / v.leg_time
        v.leg_puistoperc_time_l = comp_time / v.leg_time
        v.puisto_success = cc.leg_min_puistotime / (
            v.result.puisto_max_level * v.leg_time)

    v.save()

def update_puistoman_result_fields_2(r):
    if r.status == 0:   # A valid result
        # using filter returns an new QuerySet
        visits_qs = Visit.objects.filter(result_id=r.id)
        visits = list(visits_qs)
        r.puisto_optimum = calculate_puisto_optimum_obj(
                                visits, r.puisto_max_level)
        r.puisto_mistakes = r.time - r.puisto_optimum
    
        r.save()

# Addition by Riku on 2019-12-01 (Puistoman additions)
def calculate_puisto_max_level_obj(visits):
    # Aiming for descending order
    temp_list = sorted(visits, key=get_success_level_obj, reverse=True)
    # returns the fourth highest perc of leg_min_puistotime / leg_time
    return get_success_level_obj(temp_list[3])

# Addition by Riku on 2019-11-27 (Puistoman additions)
def get_success_level_obj(visit):
    if visit.leg_time > 0:    # A valid time
        return visit.coursecontrol.leg_min_puistotime / visit.leg_time
    else:
        return 0.1    # Small but bigger than zero for invalid.

# Addition by Riku on 2019-11-27 (Puistoman additions)
def calculate_puisto_optimum_obj(visits, puisto_max_level):
    return sum(v.leg_time for v in visits 
               if v.puisto_success 
                    and v.puisto_success >= puisto_max_level) \
                    + sum(round_time(v.coursecontrol.leg_min_puistotime
                                    / puisto_max_level)
                         for v in visits
                         if v.puisto_success
                            and v.puisto_success < puisto_max_level)

# Addition by Riku on 2019-11-27 (Puistoman additions)
def round_time(time):
    return int(time + 0.5)

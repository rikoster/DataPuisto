"""
This module calculates various interesting stats for each result of a
course. The stats are added to the course, a list_of_dicts.

Author: Riku Österman
Most recent version: 2020-11-10

"""
from .definitions import status_ok, status_manual

# Addition by Riku on 2019-11-25 (Puistoman additions)
def add_puistoman_stats(course, results_list):
    """ Top-level function, no return value. One direct actual
    calculation, calls four other functions for most calculations.
    """
    if results_list:
        # 1st - course stats
        course['puistoman_time'] \
            = sum(c['leg_min_puistotime'] for c in course['controls'])
        add_puistoman_to_coursecontrols(course['controls'])

        # 2nd - result stats
        for result in (r for r in results_list if not status_manual(r)):
            result['puisto_max_level'] = calculate_puisto_max_level(
                result['controltimes'])
            add_puistoman_stats_for_visits(
                visits=result['controltimes'],
                puisto_max_level=result['puisto_max_level'])
            if status_ok(result):
                add_puistoman_stats_per_result(
                    result=result,
                    puistoman_time=course['puistoman_time'],
                    min_puistotime=course['min_puistotime'])

# Addition by Riku on 2019-11-27 (Puistoman additions)
def add_puistoman_to_coursecontrols(coursecontrols):
    """ No return value. Function name explains itself. """
    puistoman_time = 0
    for control in coursecontrols:
        puistoman_time += control['leg_min_puistotime']
        control['puistoman_time'] = puistoman_time

# Addition by Riku on 2019-11-25 (Puistoman additions)
def add_puistoman_stats_for_visits(visits, puisto_max_level):
    """ No return value. Comp_time is the speed in 'lead'. Calls one
    function for every visit. This function does the calculations.
    """
    prev_visit = None
    for visit in visits:
        if prev_visit:
           # When there is a previous visit, compare to that
            comp_time = visit['coursecontrol']['min_puistotime'] \
                - prev_visit['coursecontrol']['min_puistotime']
        else:
           # This is the default when comparison to previous visit
           # cannot be done.
            comp_time = visit['coursecontrol']['leg_min_puistotime']
        prev_visit = visit
        add_puistoman_stats_per_visit(visit, comp_time, puisto_max_level)

# Addition by Riku on 2019-11-25 (Puistoman additions)
def add_puistoman_stats_per_visit(visit, comp_time, puisto_max_level):
    """ No return value. Calculations done for valid visits. """
    if visit['leg_time']:    # A valid visit record
        cc = visit['coursecontrol']
        visit['puistodiff_time_pm'] \
            = visit['time'] - cc['puistoman_time']
        visit['puistodiff_time_l'] \
            = visit['time'] - cc['min_puistotime']
        visit['leg_puistodiff_time_pm'] \
            = visit['leg_time'] - cc['leg_min_puistotime']
        visit['leg_puistodiff_time_l'] \
            = visit['leg_time'] - comp_time
        visit['leg_puistoperc_time_pm'] \
            = cc['leg_min_puistotime'] / visit['leg_time']
        visit['leg_puistoperc_time_l'] \
            = comp_time / visit['leg_time']
        visit['puisto_success'] \
            = cc['leg_min_puistotime'] / (puisto_max_level
                                            * visit['leg_time'])
    else:
        visit['puisto_success'] = 0.01

# Addition by Riku on 2019-11-25 (Puistoman additions)
def add_puistoman_stats_per_result(result, puistoman_time, min_puistotime):
    """ No return value. Most calculations simple, one function call.
    """
    result['puistodiff_time_pm'] = result['time'] - puistoman_time
    result['puistodiff_time_l'] = result['time'] - min_puistotime
    result['puistoperc_time_pm'] = puistoman_time / result['time']
    result['puistoperc_time_l'] = min_puistotime / result['time']
    result['puisto_success'] \
        = result['puistoperc_time_pm'] / result['puisto_max_level']
    result['puisto_optimum'] = calculate_puisto_optimum(
        visits=result['controltimes'],
        puisto_max_level=result['puisto_max_level'])
    result['puisto_mistakes'] = result['time'] - result['puisto_optimum']

# Addition by Riku on 2019-11-27 (Puistoman additions)
def calculate_puisto_max_level(visits):
    """ Returns the 4th highest perc of leg_min_puistotime / leg_time
    """
    # Aiming for descending order
    temp_list = sorted(visits, key=get_success_level, reverse=True)
    return get_success_level(temp_list[3])

# Addition by Riku on 2019-11-27 (Puistoman additions)
def get_success_level(visit):
    """ Returns success level between 0 and 1. """
    if visit['leg_time']:   # A valid visit record
        return visit['coursecontrol']['leg_min_puistotime'] \
                / visit['leg_time']
    else:
        return 0.1   # A low but non-zero for invalid visit record

# Addition by Riku on 2019-11-27 (Puistoman additions)
def calculate_puisto_optimum(visits, puisto_max_level):
    """ Returns puisto_optimum, an estimate of total time without errors.
        For those legs that the runner has matched his puisto_max_level
        (four best legs), add up leg_times, for other legs, add up an
        error-free estimate by dividing the puistoman leg time by
        puisto_max_level (a number between 0 and 1).
    """
    return sum(v['leg_time'] for v in visits
               if v['puisto_success'] >= puisto_max_level) \
                   + sum(round_time(v['coursecontrol']['leg_min_puistotime']
                                    / puisto_max_level)
                         for v in visits
                         if v['puisto_success'] < puisto_max_level)

# Addition by Riku on 2019-11-27 (Puistoman additions)
def round_time(time):
    """ Returns time in seconds (int) from float. """
    return int(time + 0.5)

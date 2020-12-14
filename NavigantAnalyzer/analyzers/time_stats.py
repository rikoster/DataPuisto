"""
This module calculates time stats for each result of a race.

Author: Riku Österman
Most recent version: 2020-11-11

"""
import statistics
from .definitions import LONGTIME, status_manual

def add_total_time_and_leg_times(course_results):
    """ Top-level function #1, does not return anything, but
    ensures that every result has a time and calculates leg times.
    """
    for result in course_results:
        # Also manual results have the time in controltimes list
        if not 'time' in result or not result['time']:
            result['time'] = result['controltimes'][-1]['time']
        if not status_manual(result):
            previous_time = 0
            for control in result['controltimes']:
                if control['time']:
                    control['leg_time'] = control['time'] - previous_time
                    previous_time = control['time']
                else:
                    control['leg_time'] = None

def add_time_stats(course, results_list, ispuisto):
    """ Top-level function #2, does not return anything, but adds basic
    time stats in place to a course via three subfunction calls. Used
    both in overall and puisto contexts (the 'ispuisto' parameter).
    """
    controls_list = course['controls']
    add_control_stats_for_var(controls_list, results_list,
                              'time', ispuisto)
    add_control_stats_for_var(controls_list, results_list,
                              'leg_time', ispuisto)
    add_course_mean_and_min_time(course, results_list, ispuisto)

#
# *****************************************
#

def add_control_stats_for_var(controls_list, results_list,
                              name_of_var, ispuisto=False):
    """ Function that calculates and stores in place mean and min stats
    for course controls, both in overall and puisto contexts.
    """
    if name_of_var == 'time':
        prefix = ''
    elif name_of_var == 'leg_time':
        prefix = 'leg_'
    if ispuisto:
        name_of_mean = prefix + 'mean_puistotime'
        name_of_min = prefix + 'min_puistotime'
    else:
        name_of_mean = prefix + 'mean_time'
        name_of_min = prefix + 'min_time'

    if results_list:
        calc_list = [r1 for r1 in results_list if
                len(r1['controltimes']) == len(controls_list)]
        for i in range(len(controls_list)):
            controls_list[i][name_of_mean] \
                = int(statistics.mean([r['controltimes'][i][name_of_var]
                                  for r in calc_list
                                  if r['controltimes'][i][name_of_var]]))
            controls_list[i][name_of_min] \
                = min(r['controltimes'][i][name_of_var]
                       for r in calc_list
                       if r['controltimes'][i][name_of_var])

def add_course_mean_and_min_time(course, results_list, ispuisto):
    """ Function that calculates and stores in place mean and min stats
    for course, both in overall and puisto contexts.
    """
    if ispuisto:
        name_of_mean = 'mean_puistotime'
        name_of_min = 'min_puistotime'
    else:
        name_of_mean = 'mean_time'
        name_of_min = 'min_time'
    if results_list:
        calc_list = [r['time'] for r in results_list
                        if r['time'] and r['time'] < LONGTIME]
        if calc_list:
            course[name_of_mean] = int(statistics.mean(calc_list))
            course[name_of_min] = min(calc_list)
        else:
            course[name_of_mean] = 0
            course[name_of_min] = 0

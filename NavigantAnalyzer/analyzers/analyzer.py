"""
This module (and other files in this folder) calculate various
interesting stats for each result of the race. Also the results of
interest are filtered from all results.

Author: Riku Österman
Most recent version: 2020-11-10

"""
import copy
import logging

from NavigantAnalyzer.models.club import Club
from NavigantAnalyzer.models.matchname import MatchName
#from .definitions import status_ok, status_manual
from .time_stats import add_total_time_and_leg_times, add_time_stats
from .position_stats import calculate_overall_positions, \
    calculate_control_positions, calculate_control_puistopositions
from .puistoman_stats import add_puistoman_stats

logger = logging.getLogger(__name__)

def get_analyzed_and_filtered_results(results):
    """ Top-level function, returns analyzed and filtered results for
    the courses, calls the main function for every competitive course.
    """
    filtered_results = copy.copy(results)
    filtered_courses = list()
    for course in results['courses']:
        if len(course['controls']) > 2:    # not 'Oma rata'
            filtered_course = get_analyzed_and_filtered_course(course)
            filtered_courses.append(filtered_course)
    filtered_results['results'] = filtered_courses
    return filtered_results

# Not needed anymore since 2020-06-14 change
#
# def create_a_list_of_ok_results(course_results):
#    return [result for result in course_results if status_ok(result)]


def get_analyzed_and_filtered_course(course):
    """ Main function of the module, returns an analyzed and filtered
    course. Proceeds step-wise in analysis.
    """
    filtered_course = copy.copy(course)
    course_results = course['results']
    filtered_course['num_participants'] = len(course_results)

    # --- Step 1. for each course: Add total & leg times ---
    add_total_time_and_leg_times(course_results)

    # --- Step 2. for each course: Sort & positions ---
    calculate_control_positions(course_results)

    # --- Step 3. Add time stats (mean, min) to controls and overall,
    #             focus stats on ok results
    # course_ok_results = create_a_list_of_ok_results(course_results)
    add_time_stats(filtered_course, course_results, ispuisto=False)

    # --- Step 4. Overall sort & positions ---
    calculate_overall_positions(course_results, 'position')

    # --- Step 5. for each course: Filter to clubs and names in the Db
    filtered_results = filter_to_clubs_and_names_in_db(course_results)
    calculate_overall_positions(filtered_results, 'puistoposition')

    # --- Step 6. for each course, calculate puistopositions per control
    calculate_control_puistopositions(filtered_results)

    # --- Step 7. Add puistostats (mean, min) to controls and overall
    #             focus stats on ok results ---
    # filtered_ok_results = create_a_list_of_ok_results(filtered_results)
    add_time_stats(filtered_course, filtered_results, ispuisto=True)

    # Addition by Riku on 2019-11-24 (Puistoman additions)
    #
    # --- Step 8. Add puistoman stats
    add_puistoman_stats(filtered_course, filtered_results)

    filtered_course['results'] = filtered_results
    return filtered_course

def filter_to_clubs_and_names_in_db(input_results):
    """ Returns a list filtered by database value matches.
    """
    matchnames = [mn.name for mn in MatchName.objects.all()]
    club_names = [club.name for club in Club.objects.all()]

    return [x for x in input_results
            if x['name'] in matchnames
            or x['club'] in club_names]

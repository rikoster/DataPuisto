"""
This module cleans orienteering results with occasional missing or
superfluous control visits.  As a result, one and only one visit record
(possibly empty) is stored for each coursecontrol. Additionally, the
coursecontrol-list representation is standardized.

Author: Riku Österman
Most recent version: 2020-11-10

"""
import logging

from .definitions import status_manual, LONGTIME

logger = logging.getLogger(__name__)

def clean_results(results):
    """ The top-level function of this module. Does not return anything,
    rather, reshapes the 'results' list_of_dicts. Calls the key
    functions per course or per result.
    """
    for course in results['courses']:
        course['begin'] = results['begin'] # Courses need the datetime
        # 'create_coursecontrols_list' is an attempt towards objects
        course_controls = create_coursecontrols_list(course['controls'])
        course['controls'] = course_controls
        if len(course_controls) > 2:    # not 'Oma rata'
            for result in course['results']:
                if not status_manual(result):
                    clean_result_v2(result, course_controls)

#
# ***********************************************************
#
def create_coursecontrols_list(cc_list):
    """ Returns a dict with key initial db fields. Standardizes the
    coursecontrols-list as a list of dicts. Ensures the existence of
    ordernumber, which is used later in the db.
    """
    # Function update on 2020-04-26 by Riku, can accept two kinds of
    # list, one of integers, and one of dicts
    if type(cc_list[0]) is int:
        return [{'ordernumber': cc[0], 'code': cc[1]}
                    for cc in enumerate(cc_list, start=1)]
    else:
        return [{'ordernumber': cc[0], **cc[1]}
                    for cc in enumerate(cc_list, start=1)]

# Added on 2019-11-30 by Riku, effort towards more object-based format
# (but not fully - not creating objects directly, but dicts)
def create_visit(coursecontrol, **kwargs):
    """ Returns a dict with key initial visit db fields. Standardizes
    the visit-list as a list of dicts. Ensures mapping to a
    coursecontrol, and the existence of ordernumber for the db.
    """
    return {'coursecontrol': coursecontrol,
            'ordernumber': coursecontrol['ordernumber'],
            **kwargs
            }

def create_missed_visit(expected_coursecontrol):
    """ Using create_visit, returns a dict without a time. Works as a
    'blank' in the list of visits.
    """
    return create_visit(
        coursecontrol=expected_coursecontrol,
        code=expected_coursecontrol['code'],
        time=None)

def get_filtered_visit_list(all_visits_index, course_controls, ascending):
    """ Returns a special format, a list of lists of visits. It is
    filtered from the input list of lists of visits, 'all_visits_index'.
    The function filters out the impossibles based on the logic of
    traversing the course controls either from beginning to end or end
    to beginning.
    """
    empties = 0
    all_visits_index_2 = list()
    if ascending:
        earliest = 0
        for i in range(len(course_controls)):
            # Filters out too early visits - cannot regard those visits
            # as valid
            control_visits_list = \
                    [v for v in all_visits_index[i] if v >= earliest]
            if len(control_visits_list) == 0: # Visit not happened
                empties += 1
            else: # visit did happen, so next visit must be later
                earliest = min(control_visits_list) + 1
            all_visits_index_2.append(control_visits_list)
    else:
        latest = 1000 # arbitrarily big number
        # The control ordernumbers in reverse order, last visit first
        for i in range(len(course_controls) - 1, -1, -1):
            # Filters out too late visits - cannot regard those visits
            # as valid
            control_visits_list = \
                    [v for v in all_visits_index[i] if v <= latest]
            if len(control_visits_list) == 0: # Visit not happened
                empties += 1
            else: # visit did happen, so previous visit must be earlier
                latest = max(control_visits_list) - 1
            all_visits_index_2.append(control_visits_list)
        # append above generates a backwards list that needs to be reversed
        all_visits_index_2.reverse()
    # empties is a quality score of the filtering
    return all_visits_index_2, empties


def clean_result_v2(result, course_controls):
    """ Does not return anything. Per a result, ensures that the visits
    received in result['controltimes'] are legitimately formatted so
    that non-visits are represented by 'missed visit' entries in the
    list, and superfluous ones are cleaned away.
    """
    all_visits = result['controltimes']

    ## Step 0. Make sure there is always a time on finish.
    ## A LONGTIME entry will eventually be written as a 'missed visit'
    if course_controls[-1]['code'] not in [entry['code'] for entry in
            all_visits]:
        all_visits.append({'code': course_controls[-1]['code'],
                             'time': LONGTIME})

    ## Step 1. Create a list of all possible visits
    all_visits_index = list()
    # ***** Possible future improvement: improve iteration so that it
    # would iterate the codes (list comprehension) instead of i.
    for i in range(len(course_controls)):
        code = course_controls[i]['code']
        control_visits_list = [v[0] for v in
                enumerate(all_visits) if v[1]['code'] == code]
        all_visits_index.append(control_visits_list)

    ## Step 2. Study from the start - filter out those visits that were
    ## too early in order
    all_visits_index_2, empties_2 = get_filtered_visit_list(
            all_visits_index, course_controls, ascending=True)

    ## Step 3. Study from the end - filter out those visits that were
    ## too late in order
    all_visits_index_3, empties_3 = get_filtered_visit_list(
            all_visits_index, course_controls, ascending=False)

    ## Step 4. Select either Step 2 outcome or Step 3, whichever is a
    ## better match to the track
    if empties_2 <= empties_3:
        all_visits_index = all_visits_index_2
    else:
        # Filter out too early visits to ensure that the logic of
        # min-function in Step 5. makes right choices
        all_visits_index, empties = get_filtered_visit_list(
                all_visits_index_3, course_controls, ascending=True)

    ## Step 5. Create the clean list of visits based on the filtered
    ## visit index
    clean_entries = list()
    for i_list in enumerate(all_visits_index):
        i = i_list[0]
        cc = course_controls[i]
        # i_list[1] is a (possibly empty) list of indices (int)
        if i_list[1]:
            # Record the first visit of possible ones
            j = min(i_list[1])
            visit = all_visits[j]
            entry = create_visit(coursecontrol=cc, **visit)
        else:
            entry = create_missed_visit(cc)

        clean_entries.append(entry)

    ## Step 6. Save the result to right place
    result['controltimes'] = clean_entries

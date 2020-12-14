"""
This module calculates position stats for each result of a race.

Author: Riku Österman
Most recent version: 2020-11-11

"""
from .definitions import LONGTIME, status_ok, status_manual

def calculate_overall_positions(course_results, name_of_position):
    """ Top-level function #1, does not return anything, but sorts
    and stores position in place (position or puistoposition).
    """
    course_results.sort(key=get_time)
    add_position(course_results, name_of_position, get_time)

def calculate_control_positions(course_results):
    """ Top-level function #2, does not return anything, but
    stores overall and leg position in place for each result.
    """
    if course_results:    # Not empty list
        # Using the first valid result here,
        # other valid results would give the same
        try:
            # STEP 0 - determine the length of course
            valid_result = next(result for result in course_results
                                if status_ok(result))
            length_of_course = len(valid_result['controltimes'])

            for ctrl_index in range(length_of_course):

                # For each control STEP 1: prepare the two sorts
                for result in course_results:
                    if not status_manual(result):
                        decorate_with_control(result, ctrl_index)

                # For each control STEP 2: Sort and position calc 1.
                sorted_results = sorted(course_results, key=get_sort1)
                add_position(sorted_results, 'position1', get_sort1)

                # For each control STEP 3: Sort and position calc 2.
                sorted_results = sorted(course_results, key=get_sort2)
                add_position(sorted_results, 'position2', get_sort2)

                # For each control STEP 4: Store calculation results
                for result in course_results:
                    if not status_manual(result):
                        store_position_with_control(result, ctrl_index)

        except StopIteration:
            # No valid results in course, no point in calculating
            pass

def calculate_control_puistopositions(filtered):
    """ Top-level function #3, does not return anything, but
    stores overall and leg puistoposition in place for each result.
    """
    if filtered:    # Not empty list
        # Using the first valid result here,
        # other valid results would give the same
        try:
            # STEP 0 - determine the length of course
            valid_result = next(result for result in filtered
                                if status_ok(result))
            length_of_course = len(valid_result['controltimes'])

            for ctrl_index in range(length_of_course):

                # For each control STEP 1: prepare the two sorts
                for result in filtered:
                    if not status_manual(result):
                        decorate_with_control(result, ctrl_index)

                # For each control STEP 2: Sort and position calc 1.
                sorted_results = sorted(filtered, key=get_sort1)
                add_position(sorted_results, 'position1', get_sort1)

                # For each control STEP 3: Sort and position calc 2.
                sorted_results = sorted(filtered, key=get_sort2)
                add_position(sorted_results, 'position2', get_sort2)

                # For each control STEP 4: Store calculation results
                for result in filtered:
                    if not status_manual(result):
                        store_puistoposition_with_control(result, ctrl_index)

        except StopIteration:
            # No valid results in course, no point in calculating
            pass

def get_time(result):
    """ One of the three key_func for sort. (1/3) """
    if status_ok(result) or status_manual(result):
        return result['time']
        # return result['time'] if result['time'] else LONGTIME
    else:
        return LONGTIME # LONGTIME sufficiently much

def get_sort1(result):
    """ One of the three key_func for sort. (2/3) """
    if not status_manual(result) and result['sort1']:
        return result['sort1']
    else:
        return LONGTIME # LONGTIME sufficiently much

def get_sort2(result):
    """ One of the three key_func for sort. (3/3) """
    if not status_manual(result) and result['sort2']:
        return result['sort2']
    else:
        return LONGTIME # LONGTIME sufficiently much

def add_position(results_list, name_of_position, key_func):
    """ Position calculator function, stores results in place. """
    # 'time' can be legtime, overall time, ... three different key_func
    # are used in calling this function.
    time = 0
    prev_time = 0
    # 'position' can be position, position1 or position2, passed in
    # 'name_of_position'. position1 and position2 are temporary storages
    # for control positions.
    position = 0
    # 'results_list' is already properly sorted with the right key_func
    for result in enumerate(results_list, start=1):
        # Three possibilities, time used in determining
        time = key_func(result[1])
        # CASE 1: Position none, something wrong with the result
        if time == LONGTIME:
            position = None
        # CASE 2: Base case, position the same as in enumerated list
        elif time > prev_time:
            position = result[0]
        # CASE 3: No else clause needed, if same time, position same
        # as with previous result. (time never smaller than prev_time)
        result[1][name_of_position] = position
        # Needed for CASE 2 comparison in next iteration
        prev_time = time

def decorate_with_control(result, ctrl_index):
    """ Function used in preparation for sort. """
    try:
        result['sort1'] = result['controltimes'][ctrl_index]['time']
        result['sort2'] = result['controltimes'][ctrl_index]['leg_time']
    except: # it is possible that some results don't have visits
        result['sort1'] = LONGTIME
        result['sort2'] = LONGTIME

def store_position_with_control(result, ctrl_index):
    """ Function used in storing calculated positions in-place. """
    try:
        result['controltimes'][ctrl_index]['position'] = result['position1']
        result['controltimes'][ctrl_index]['leg_position'] = result['position2']
    except: # it is possible that some results don't have visits
        pass

def store_puistoposition_with_control(result, ctrl_index):
    """ Function used in storing calculated puistopositions in-place. """
    try:
        result['controltimes'][ctrl_index]['puistoposition'] = result['position1']
        result['controltimes'][ctrl_index]['leg_puistoposition'] = result['position2']
    except: # it is possible that some results don't have visits
        pass

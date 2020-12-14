import requests
import json
from NavigantAnalyzer.common import get_fromtimestamp, datetime_string
DTFORMAT_S = '%Y-%m-%d %H:%M:%S'

import logging

logger = logging.getLogger(__name__)


EVENT_API_URL = 'https://www.rastilippu.fi/api/events/searchresult/uuid/{}'
COURSE_API_URL = 'https://www.rastilippu.fi/api/results/event/{}/courses'
RESULTS_API_URL = 'https://www.rastilippu.fi/api/results/event/{}/courses/{}'

def rastilippu_download(url):
    event_id = url.split("/")[-3]
    course_id = url.split("/")[-1]
    try:
        # Step 1 - Race data
        api_url = EVENT_API_URL.format(event_id)
        response = requests.get(api_url)
        raw_dict = json.loads(response.text)
        
        # Step 2 - Course data
        api_url = COURSE_API_URL.format(event_id)
        response = requests.get(api_url)
        all_courses = json.loads(response.text)
        course = get_course(course_id, all_courses)

        # Step 3 - Results data
        api_url = RESULTS_API_URL.format(event_id, course_id)
        response = requests.get(api_url)
        results = json.loads(response.text)
        course['results'] = results

        logger.info(f"--- len(results) {len(results)}")

        raw_dict['courses'] = [course]

        new_dict = convert_rastilippu(raw_dict)

        return new_dict
        # return convert_rastilippu(raw_dict)

    except:
        return dict()

def get_course(course_id, all_courses):
    filtered = [c for c in all_courses if c['courseId'] == course_id]
    if filtered: # Not an empty list
        return filtered[0]
    else:
        return dict()

def convert_rastilippu(orig):
    conv = dict()

    # Step 1 - Convert the race data to NaviSport format
    conv['uuid'] = orig['uuid']
    conv['name'] = orig['name']
    conv['serie'] = orig['parentSeriesEventName']
    unix_timestamp = orig['startDateTime']/1000
    conv['begin'] = datetime_string(get_fromtimestamp(unix_timestamp), DTFORMAT_S)

    # Step 2 - Convert the course data to NaviSport format
    orig_course = orig['courses'][0]
    orig_controls = orig_course['controls']
    # Convert strings to integers
    conv_controls = [int(c) for c in orig_controls]
    conv_course = orig_course
    conv_course['controls'] = conv_controls
    
    # Step 3 - Convert the results to NaviSport format
    orig_results = orig_course['results']
    conv_results = list()
    for orig_result in orig_results:
        conv_result = dict()
        conv_result['name'] = orig_result['name']
        conv_result['club'] = orig_result['club']
        conv_result['emit'] = orig_result['emitNumber']

        # Changed 2020-04-26 by Riku, with NaviSport changes
        # Status does not have to be a number anymore.
        conv_result['status'] = orig_result['status']

#        if orig_result['status'] == "OK":
#            conv_result['status'] = 0
#        elif orig_result['status'] == "DSQ":
#            conv_result['status'] = 3
#        else:
#            conv_result['status'] = 1
        
        conv_result['starttime'] = "{} {}".format(orig_result['startTime']['date'],
                                                  orig_result['startTime']['time'])
        conv_result['readtime'] = "{} {}".format(orig_result['readTime']['date'],
                                                 orig_result['readTime']['time'])
        orig_controltimes = orig_result['controlTimes']
        conv_controltimes = [create_dict_in_int(ct) for ct in orig_controltimes]
        conv_result['controltimes'] = conv_controltimes

        conv_results.append(conv_result)

    conv_course['results'] = conv_results
    conv['courses'] = [conv_course]

    return conv

def create_dict_in_int(ct):
    r = dict()
    r['code'] = int(ct['code'])
    r['time'] = ct['time']
    return r

import requests
import json
import logging

import environ

from NavigantAnalyzer.common import aware_datetime

logger = logging.getLogger(__name__)

env = environ.Env(ON_GCLOUD=(bool, False))
if not env('ON_GCLOUD'):
    environ.Env.read_env()
API_URL = env('NAVISPORT_API_URL')

def get_event_uuid(url):
    # UUID:s are 36 characters long
    # Order of checking matters here
    s = url.split("/")
    if len(s[-3]) == 36:
        return s[-3]
    elif len(s[-1]) == 36:
        return s[-1]
    elif (s[-2]) == 36:
        return s[-2]
    else:
        return None

def navisport_download(url):
    event_id = get_event_uuid(url)
    try:
        event_url = f"{API_URL}/{event_id}"
        response = requests.get(event_url)
        event_dict = json.loads(response.text)

        courses_url = f"{event_url}/courses"
        response = requests.get(courses_url)
        courses_dict = json.loads(response.text)
        
        results_url = f"{event_url}/results"
        response = requests.get(results_url)
        results_dict = json.loads(response.text)

        new_dict = convert_navisport(event_dict,
                                    courses_dict,
                                    results_dict)

        return new_dict

    except:
        return dict()

def get_standard_dt(dt_string):
    return dt_string[:19] if dt_string else None

def convert_navisport(event, courses, results):
    conv = dict()

    conv['uuid'] = event['id']
    conv['name'] = event['name']
    conv['serie'] = event['series']['name']
    conv['begin'] = get_standard_dt(event['begin'])
    conv['courses'] = \
            convert_navisport_courses(courses, results)
    return conv

def convert_navisport_courses(orig_courses, orig_results):
    conv_courses = list()
    for orig_course in orig_courses:
        conv_course = dict()
        # Occasionally in NaviSport some controls have two different codes, or letters
        convert_list = get_convert_list(orig_course['controls'])

        conv_course['name'] = orig_course['name']
        conv_course['length'] = orig_course['distance']
        conv_course['results'] = \
            convert_navisport_results(orig_results, orig_course, convert_list)
        conv_course['controls'] = \
                convert_navisport_codes(orig_course['controls'], convert_list)

        conv_courses.append(conv_course)

    return conv_courses

def convert_navisport_results(orig_results, course, convert_list):
    conv_results = list()
    
    for orig_result in (r for r in orig_results 
            if r['courseId'] == course['id'] and r['controlTimes']):
        conv_result = dict()
        conv_result['name'] = orig_result['name']
        conv_result['club'] = orig_result['club']
        conv_result['emit'] = orig_result['chip']
        conv_result['status'] = orig_result['status']
        conv_result['time'] = orig_result['time']
        conv_result['starttime'] = \
                get_standard_dt(orig_result['startTime'])
        conv_result['readtime'] = \
                get_standard_dt(orig_result['readTime'])
        if convert_list:
            conv_result['controltimes'] = \
                convert_navisport_codes(orig_result['controlTimes'], convert_list)
        else:
            conv_result['controltimes'] = orig_result['controlTimes']
        if orig_result['status'] == 'Manual':
            conv_result['controltimes'] = \
                    [{
                        'code': get_final_control_code(course['controls']),
                        'time': get_time_from_timestamps(orig_result)
                    }]

        conv_results.append(conv_result)

    return conv_results

# More robust NaviSport multiple-codes conversion 
# written by Riku on 2020-10-08
#
def convert_navisport_codes(controltimes, convert_list):
    if controltimes:
        check_list = [c[0] for c in convert_list]
        for cc in controltimes:
            if type(cc['code']) == list:
                cc['code'] = cc['code'][0]
            elif cc['code'] in check_list:
                cc['code'] = get_convert_code(cc['code'], convert_list)
    return controltimes

# More robust NaviSport multiple-codes conversion 
# written by Riku on 2020-10-08
#
def get_convert_list(controls):
    result = list()
    for cc in controls:
        if type(cc['code']) == list:
            for i in range(1, len(cc['code'])): # always >= 2
                conv = [cc['code'][i], cc['code'][0]]
                result.append(conv)
        elif type(cc['code']) != int:
             # Assuming it is a string, and using the last character
            new_code = 4000 + ord(cc['code'][-1])
            conv = [cc['code'], new_code]
            cc['code'] = new_code # Need to change also the original
            result.append(conv)
    return result

def get_convert_code(code, convert_list):
    return next(c[1] for c in convert_list if c[0] == code)

def get_final_control_code(controls):
    return controls[-1]['code'] # The code of the last control

# for Navisport Manual results / written by Riku on 2020-04-16
def get_time_from_timestamps(result):
    start_str = get_standard_dt(result['registerTime'])
    start = aware_datetime(start_str)
    end_str = get_standard_dt(result['readTime'])
    end = aware_datetime(end_str)
    return int((end - start).total_seconds())


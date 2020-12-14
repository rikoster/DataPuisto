import requests
import json

API_URL = 'https://navisport.fi/api/events'

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
    #try:
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

    #except:
        #return dict()

def get_standard_dt(dt_string):
    return dt_string[:19] if dt_string else None

def convert_navisport(event, courses, results):
    conv = dict()

    conv['uuid'] = event['id']
    conv['name'] = event['name']
    conv['serie'] = event['series']['name']

    conv['begin'] = get_standard_dt(event['begin'][:19])
    conv['courses'] = \
            convert_navisport_courses(courses, results)
    return conv

# Temporary function on 2020-05-05 to remove false code
def check_f1(c):
    r = dict()
    for key, value in c.items():
        if key == 'code':
            if value == 'F1':
                r['code'] = 100
            else:
                r['code'] = int(value)
        else:
            r[key] = value
    return r

def convert_navisport_courses(orig_courses, orig_results):
    conv_courses = list()
    for orig_course in orig_courses:
        conv_course = dict()
        conv_course['name'] = orig_course['name']
        conv_course['length'] = orig_course['distance']
        # conv_course['controls'] = orig_course['controls']
        # Temporary change on 2020-05-05 to remove false code
        conv_course['controls'] = \
                [check_f1(c) for c in orig_course['controls']]
        conv_course['results'] = \
            convert_navisport_results(orig_results, orig_course['id'])

        conv_courses.append(conv_course)

    return conv_courses

def convert_navisport_results(orig_results, course_id):
    conv_results = list()
    for orig_result in (r for r in orig_results 
            if r['courseId'] == course_id):
        conv_result = dict()
        conv_result['name'] = orig_result['name']

        conv_result['club'] = orig_result['club']
        conv_result['emit'] = orig_result['chip']
        conv_result['status'] = orig_result['status']
        conv_result['starttime'] = \
                get_standard_dt(orig_result['startTime'])
        conv_result['readtime'] = \
                get_standard_dt(orig_result['readTime'])
        # conv_result['controltimes'] = orig_result['controlTimes']
        # Temporary change on 2020-05-05 to remove false code
        conv_result['controltimes'] = \
                [check_f1(c) for c in orig_result['controlTimes']]

        conv_results.append(conv_result)

    return conv_results

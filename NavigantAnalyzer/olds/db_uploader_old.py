from NavigantAnalyzer.models import Course, Coursecontrols, Result,\
        MatchName, Runner, Visit
from NavigantAnalyzer.common import aware_datetime
from NavigantAnalyzer.analyzer import status_manual

from datetime import datetime

LONGTIME = 28800

def get_matching_runner(name_text):
    match = MatchName.objects.filter(name=name_text).first()
    if match:
        return match.runner
    else:
        return None


def upload_results(club_results):

    race = club_results['race']

    for course in club_results['results']:
        c = create_course(course, race=race)
        cc_list = list()
        for control in course['controls']:
            ctrl = create_coursecontrols(control, course=c)
            ctrl.save()
            cc_list.append(ctrl)
        for result in course['results']:
            rs = create_result(result, course=c)
            if 'controltimes' in result and not status_manual(result):
                for visit in result['controltimes']:
                    cc = next(ctrl for ctrl in cc_list
                              if ctrl.ordernumber == visit['ordernumber'])
                    v = create_visit(visit, result=rs, coursecontrol=cc)

def create_course(extended_dict, race):
    course = Course(race=race, name=extended_dict['name'])
    course.begin = race.begin  # Added on 2019-12-04 for Puistoserie sort
    for key, value in extended_dict.items():
        if hasattr(course, key) and key != 'id':
            setattr(course, key, value)
    course.save()
    return course

def create_coursecontrols(extended_dict, course):
    code = extended_dict['code']
    code = code if str(code).isnumeric() else 100
    cc = Coursecontrols(course=course, 
                        ordernumber=extended_dict['ordernumber'],
                        code=code)
    for key, value in extended_dict.items():
        if hasattr(cc, key) and key not in ['id', 'code']:
            setattr(cc, key, value)
    cc.save()
    return cc

def create_result(extended_dict, course):
    rnnr = get_matching_runner(extended_dict['name']) # None if no match
    if extended_dict['starttime']:
        start_time = aware_datetime(extended_dict['starttime'])
    else:
        start_time = None
    if extended_dict['readtime']:
        read_time = aware_datetime(extended_dict['readtime'])
    else:
        read_time = None
    rs = Result(course=course, 
                runner=rnnr, 
                start_time=start_time,
                read_time=read_time)
    for key, value in extended_dict.items():
        if hasattr(rs, key) and key not in ['id', 'course']:
            setattr(rs, key, value)
    # Added by Riku on 2020-10-09
    if rs.time == LONGTIME:
        rs.time = None
    rs.save()
    return rs

def create_visit(extended_dict, result, coursecontrol):
    v = Visit(result=result,
              coursecontrol=coursecontrol,
              ordernumber=extended_dict['ordernumber'],
              code=extended_dict['code'])
    if extended_dict['time'] and extended_dict['time'] < LONGTIME:
        for key, value in extended_dict.items():
            if hasattr(v, key) and key not in ['id', 'code', 'coursecontrol']:
                setattr(v, key, value)
    v.save()
    return v

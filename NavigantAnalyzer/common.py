from datetime import datetime, timedelta
from django.utils import timezone
import pytz

DTFORMAT_S = '%Y-%m-%d %H:%M:%S'
DTFORMAT_T = '%Y-%m-%dT%H:%M:%S'
DTFORMAT_TZ = '%Y-%m-%dT%H:%M:%S%z'
DTFORMAT_M = '%Y-%m-%d %H:%M'
DTFORMAT_D = '%Y-%m-%d'

def time_string(time_seconds):
    if time_seconds is not None:
        if time_seconds >= 3600:        # if hour or more
            return str(timedelta(seconds=time_seconds))
        else:
            mins, secs = divmod(time_seconds, 60)
            return "{}".format(mins) + ':' + "{:02d}".format(secs)
    else:
        return ""

def aware_datetime(dt_string):
    frmt = DTFORMAT_T if dt_string[10] == 'T' else DTFORMAT_S
    return timezone.make_aware(datetime.strptime(dt_string, frmt))

def aware_datetime_tz(dt_string):
    return timezone.make_aware(datetime.strptime(dt_string, DTFORMAT_TZ))

def aware_datetime_d(dt_string):
    return timezone.make_aware(datetime.strptime(dt_string, DTFORMAT_D))

def datetime_string(dt_object, format=DTFORMAT_M):
    d = dt_object.astimezone(tz=timezone.get_current_timezone())
    return d.strftime(format)

def seconds_from_now(dt_object):
    d = dt_object.astimezone(tz=timezone.get_current_timezone())
    n = timezone.now()
    return (d - n).total_seconds()

def get_fromtimestamp(timestamp):
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(tz=timezone.get_current_timezone())

# [Added 2019-04-18]
def get_strava_date(strava_dt_string, strava_tz):
    #Only the last part of strava tz string
    tz = strava_tz.split(" ")[-1]
    #Strip the last unnecessary character - strava adds an incorrect 'Z'
    dt_string = strava_dt_string[:-1]
    
    return timezone.make_aware(
        value=datetime.strptime(dt_string, DTFORMAT_T),
        timezone=pytz.timezone(tz)
        )

# [Added 2019-04-19]
#def get_midnight_on_the_same_day(dt_object):
#    return datetime.combine(dt_object.date(), datetime.min.time())

#def get_first_day_of_week(dt_object):
#    # weekday-function gives 0 for Monday, 1 for Tuesday etc.
#    days_after_monday = dt_object.weekday()
#    td_days_after_monday = timedelta(days=days_after_monday)
#    dt_midnight = get_midnight_on_the_same_day(dt_object)
#    dt_monday = dt_midnight - td_days_after_monday
#    return timezone.make_aware(dt_monday)

# [Note 2019-04-18] Not sure if actively used
def convert_datetime_string(dt_string, format=DTFORMAT_S):
    if dt_string[-3] == ':':
        dt_string = dt_string[:-3] + dt_string[-2:]
    dt_object = datetime.strptime(dt_string, DTFORMAT_TZ)
    return datetime_string(dt_object, format=format)

# This is copied from StackOverflow.
# 'Make sure you have reverse proxy (if any) configured correctly
# (e.g. mod_rpaf installed for Apache).'
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

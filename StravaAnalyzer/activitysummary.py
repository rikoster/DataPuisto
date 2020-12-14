from StravaAnalyzer.models import Athlete, Activity, ActivitySummary, SummaryTotal
from StravaAnalyzer.stravasettings import EARLIEST_TO_UPDATE
from django.db.models import Count, Sum, Avg, Max
from django.db.models.functions import ExtractYear, ExtractQuarter, ExtractMonth, ExtractIsoYear, ExtractWeek

from django.utils import timezone
from datetime import date, datetime, timedelta
import copy

def update_or_create_activity_summaries():
    update_or_create_annual_activity_summaries()
    update_or_create_quarterly_activity_summaries()
    update_or_create_monthly_activity_summaries()
    update_or_create_weekly_activity_summaries()
    update_or_create_summarytotals()

#
# -------------------------------------------------------------------
#
# Core functions for creating Activity Summaries
#
# -------------------------------------------------------------------

def update_or_create_activity_summaries_total(
            summary_type, set_periodic_summary_fields, q_param, frame):

    q_time = enumerate(q_param.order_by('-sum_elapsed_time'), start=1)

    for element in q_time:
        entry = copy.copy(element[1])
        entry['sport_type'] = 'Total'
        entry['rank_time'] = element[0]
        entry = set_common_summary_fields(summary_type, frame, entry)
        entry = set_periodic_summary_fields(entry, frame)
        ActivitySummary.objects.update_or_create(defaults=entry, id=entry['id'])

def update_or_create_activity_summaries_per_type(
            summary_type, set_periodic_summary_fields, q_param, frame):
    
    q_time = enumerate(q_param.order_by('-sum_elapsed_time'), start=1)
    l_distance = list(enumerate(q_param.order_by('-sum_distance'), start=1))
    max_q = q_param.aggregate(Max('sum_distance')) 

    for element in q_time:
        entry = copy.copy(element[1])
        entry['sport_type'] = entry['type']
        del entry['type']
        entry['rank_time'] = element[0]
        if max_q['sum_distance__max'] > 0:   # Rank distance only when it counts
            entry['rank_distance'] = get_distance_rank(
                                        l_distance, entry['athlete'])
        entry = set_common_summary_fields(summary_type, frame, entry)
        entry = set_periodic_summary_fields(entry, frame)
        ActivitySummary.objects.update_or_create(defaults=entry, id=entry['id'])

def get_distance_rank(distance_enum_list, athlete_id):
    athlete_item = [item for item in distance_enum_list 
                        if item[1]['athlete'] == athlete_id]
    return athlete_item[0][0]    #rank is the first part of the item



def set_common_summary_fields(summary_type, frame, entry):
    entry['id'] = get_summary_id(summary_type, frame, entry)
    entry['summary_type'] = summary_type
    entry['athlete'] = Athlete.objects.get(id=entry['athlete'])
    return entry

def get_summary_id(summary_type, frame, entry):
    if summary_type == 'A':
        period_id = 'A'
    elif summary_type =='Q':
        period_id = 'Q{}'.format(frame['quarter'])
    elif summary_type == 'M':
        period_id = 'M{}'.format(frame['month'])
    elif summary_type == 'W':
        period_id = 'W{}'.format(frame['week'])
    return "{}-{}-{}-{}".format(
        entry['athlete'],
        frame['year'],
        period_id,
        entry['sport_type']
        )

#
# -------------------------------------------------------------------
#
# Calculating the stats by enhancing querysets
#
# -------------------------------------------------------------------

def create_stats_qs(q):
    return q.annotate(
            activity_count=Count('id'),
            sum_elapsed_time=Sum('elapsed_time'),
            sum_distance=Sum('distance')        
            )

#def create_total_athlete_stats_qs(q):
#    return q.values('athlete').annotate(
#            activity_count=Count('athlete'),
#            sum_elapsed_time=Sum('elapsed_time'),
#            sum_distance=Sum('distance')        
#            )

#def create_per_type_athlete_stats_qs(q):
#    return q.values('type', 'athlete').annotate(
#            activity_count=Count('athlete'),
#            sum_elapsed_time=Sum('elapsed_time'),
#            sum_distance=Sum('distance')        
#            )

#
# -------------------------------------------------------------------
#
# Annual activity summaries
#
# -------------------------------------------------------------------

def update_or_create_annual_activity_summaries():
    SUMMARY_TYPE = 'A'
    SET_PERIODIC_SUMMARY_FIELDS = set_annual_summary_fields
    q_base = Activity.objects.filter(
            start_date__gte=EARLIEST_TO_UPDATE
            ).annotate(
            year=ExtractYear('start_date')
            )
    q_stats = create_stats_qs(q_base.values('athlete'))
    q_pt_stats = create_stats_qs(q_base.values('type', 'athlete'))

    q_year = q_base.values('year').distinct()
    for frame in q_year:
        q = q_stats.filter(year=frame['year'])
        update_or_create_activity_summaries_total(
            SUMMARY_TYPE, SET_PERIODIC_SUMMARY_FIELDS, q, frame)
    
    q_type_year = q_base.values('type', 'year').distinct()
    for frame in q_type_year:
        q = q_pt_stats.filter(type=frame['type'], year=frame['year'])
        update_or_create_activity_summaries_per_type(
            SUMMARY_TYPE, SET_PERIODIC_SUMMARY_FIELDS, q, frame)

def set_annual_summary_fields(entry, frame):
    entry['year'] = frame['year']
    entry['dt_start'] = get_first_day_of_year(entry['year'])
    entry['dt_end'] = get_first_day_of_year(entry['year'] + 1)
    entry['quarter'] = None
    entry['month'] = None
    entry['week'] = None
    return entry

def get_first_day_of_year(year):
    return timezone.make_aware(datetime(year=year, month=1, day=1))

#
# -------------------------------------------------------------------
#
# Quarterly activity summaries
#
# -------------------------------------------------------------------

def update_or_create_quarterly_activity_summaries():
    SUMMARY_TYPE = 'Q'
    SET_PERIODIC_SUMMARY_FIELDS = set_quarterly_summary_fields

    q_base = Activity.objects.filter(
            start_date__gte=EARLIEST_TO_UPDATE
            ).annotate(
            year=ExtractYear('start_date'),
            quarter=ExtractQuarter('start_date')
            )
    q_stats = create_stats_qs(q_base.values('athlete'))
    q_pt_stats = create_stats_qs(q_base.values('type', 'athlete'))

    q_quarter = q_base.values('year', 'quarter').distinct()
    for frame in q_quarter:
        q = q_stats.filter(year=frame['year'], 
                           quarter=frame['quarter'])
        update_or_create_activity_summaries_total(
            SUMMARY_TYPE, SET_PERIODIC_SUMMARY_FIELDS, q, frame)
    
    q_type_quarter = q_base.values('type', 'year', 'quarter').distinct()
    for frame in q_type_quarter:
        q = q_pt_stats.filter(type=frame['type'], 
                              year=frame['year'],
                              quarter=frame['quarter'])
        update_or_create_activity_summaries_per_type(
            SUMMARY_TYPE, SET_PERIODIC_SUMMARY_FIELDS, q, frame)

def set_quarterly_summary_fields(entry, frame):
    entry['year'] = frame['year']
    entry['quarter'] = frame['quarter']
    entry['dt_start'] = get_first_day_of_quarter(
        entry['year'], entry['quarter'])
    entry['dt_end'] = get_first_day_of_next_quarter(
        entry['year'], entry['quarter'])
    entry['month'] = None
    entry['week'] = None
    return entry

def get_first_day_of_quarter(year, quarter):
    # {'1': 1, '2': 4, '3': 7, '4': 10}
    month = (quarter * 3) - 2 
    return timezone.make_aware(datetime(year=year, month=month, day=1))

def get_first_day_of_next_quarter(year, quarter):
    # {'1': 4, '2': 7, '3': 10, '4': year + 1, 1}
    month = (quarter * 3) + 1
    if month == 13:
        return timezone.make_aware(datetime(year=year + 1, month=1, day=1))
    else:
        return timezone.make_aware(datetime(year=year, month=month, day=1))

#
# -------------------------------------------------------------------
#
# Monthly activity summaries
#
# -------------------------------------------------------------------

def update_or_create_monthly_activity_summaries():
    SUMMARY_TYPE = 'M'
    SET_PERIODIC_SUMMARY_FIELDS = set_monthly_summary_fields

    q_base = Activity.objects.filter(
            start_date__gte=EARLIEST_TO_UPDATE
            ).annotate(
            year=ExtractYear('start_date'),
            month=ExtractMonth('start_date')
            )
    q_stats = create_stats_qs(q_base.values('athlete'))
    q_pt_stats = create_stats_qs(q_base.values('type', 'athlete'))

    q_month = q_base.values('year', 'month').distinct()
    for frame in q_month:
        q = q_stats.filter(year=frame['year'], 
                           month=frame['month'])
        update_or_create_activity_summaries_total(
            SUMMARY_TYPE, SET_PERIODIC_SUMMARY_FIELDS, q, frame)
    
    q_type_month = q_base.values('type', 'year', 'month').distinct()
    for frame in q_type_month:
        q = q_pt_stats.filter(type=frame['type'], 
                              year=frame['year'],
                              month=frame['month'])
        update_or_create_activity_summaries_per_type(
            SUMMARY_TYPE, SET_PERIODIC_SUMMARY_FIELDS, q, frame)

def set_monthly_summary_fields(entry, frame):
    entry['year'] = frame['year']
    entry['month'] = frame['month']
    entry['dt_start'] = get_first_day_of_month(
        entry['year'], entry['month'])
    entry['dt_end'] = get_first_day_of_next_month(
        entry['year'], entry['month'])
    entry['quarter'] = None
    entry['week'] = None
    return entry

def get_first_day_of_month(year, month):
    return timezone.make_aware(datetime(year=year, month=month, day=1))

def get_first_day_of_next_month(year, month):
    if month == 12:
        return timezone.make_aware(datetime(year=year + 1, month=1, day=1))
    else:
        return timezone.make_aware(datetime(year=year, month=month + 1, day=1))

#
# -------------------------------------------------------------------
#
# Weekly activity summaries
#
# -------------------------------------------------------------------

def update_or_create_weekly_activity_summaries():
    SUMMARY_TYPE = 'W'
    SET_PERIODIC_SUMMARY_FIELDS = set_weekly_summary_fields

    dt_early_monday = get_first_day_of_next_week_on_dt(
                                        EARLIEST_TO_UPDATE)
    q_base = Activity.objects.filter(
            start_date__gte=dt_early_monday
            ).annotate(
            year=ExtractIsoYear('start_date'),
            week=ExtractWeek('start_date')
            )
    q_stats = create_stats_qs(q_base.values('athlete'))
    q_pt_stats = create_stats_qs(q_base.values('type', 'athlete'))

    q_week = q_base.values('year', 'week').distinct()
    for frame in q_week:
        q = q_stats.filter(year=frame['year'], 
                           week=frame['week'])
        update_or_create_activity_summaries_total(
            SUMMARY_TYPE, SET_PERIODIC_SUMMARY_FIELDS, q, frame)
    
    q_type_week = q_base.values('type', 'year', 'week').distinct()
    for frame in q_type_week:
        q = q_pt_stats.filter(type=frame['type'], 
                              year=frame['year'],
                              week=frame['week'])
        update_or_create_activity_summaries_per_type(
            SUMMARY_TYPE, SET_PERIODIC_SUMMARY_FIELDS, q, frame)

def set_weekly_summary_fields(entry, frame):
    entry['year'] = frame['year']
    entry['week'] = frame['week']
    entry['dt_start'] = get_first_day_of_week(
        entry['year'], entry['week'])
    entry['dt_end'] = get_first_day_of_next_week(
        entry['year'], entry['week'])
    entry['quarter'] = None
    entry['month'] = None
    return entry

def get_monday_of_week_one(year):
    #Jan 4 is guaranteed to be in the ISO Week 1
    dt_jan_4 = datetime(year, 1, 4)
    # weekday-function gives 0 for Monday, 1 for Tuesday etc.
    days_after_monday = dt_jan_4.weekday()
    return dt_jan_4 - timedelta(days=days_after_monday)

def get_first_day_of_week(year, week):
    dt_monday = get_monday_of_week_one(year) + timedelta(weeks=week - 1)
    return timezone.make_aware(dt_monday)

def get_first_day_of_next_week(year, week):
    dt_monday = get_monday_of_week_one(year) + timedelta(weeks=week)
    return timezone.make_aware(dt_monday)

def get_midnight_on_the_same_day(dt_object):
    return datetime.combine(dt_object.date(), 
                            datetime.min.time(),
                            dt_object.tzinfo)

def get_first_day_of_next_week_on_dt(dt_object):
    #Step 1 Getting Monday
    dt_midnight = get_midnight_on_the_same_day(dt_object)
    # weekday-function gives 0 for Monday, 1 for Tuesday etc.
    days_after_monday = dt_midnight.weekday()
    dt_monday = dt_midnight - timedelta(days=days_after_monday)

    return dt_monday + timedelta(weeks=1)

#
# -------------------------------------------------------------------
#
# SummaryTotal
#
# -------------------------------------------------------------------

def update_or_create_summarytotals():
    q = ActivitySummary.objects.filter(
            dt_start__gte=EARLIEST_TO_UPDATE,
            ).values(
                'summary_type', 
                'year',
                'quarter',
                'month',
                'week',
                'sport_type',
                'dt_start', 
                'dt_end'
                ).annotate(
                    avg_activity_count=Avg('activity_count'),
                    avg_elapsed_time=Avg('sum_elapsed_time'),
                    avg_distance=Avg('sum_distance')
                    )
    for element in q:
        summarytotal = SummaryTotal(
            id=get_summarytotal_id(element),
            **element
            )
        summarytotal.save()

def get_summarytotal_id(element):
    if element['summary_type'] == 'A':
        period_id = 'A'
    elif element['summary_type'] =='Q':
        period_id = 'Q{}'.format(element['quarter'])
    elif element['summary_type'] == 'M':
        period_id = 'M{}'.format(element['month'])
    elif element['summary_type'] == 'W':
        period_id = 'W{}'.format(element['week'])
    return "{}-{}-{}".format(
        element['year'],
        period_id,
        element['sport_type']
        )

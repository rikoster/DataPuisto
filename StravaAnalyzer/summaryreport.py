from StravaAnalyzer.models import ActivitySummary, SummaryReport, SummaryColumn
from StravaAnalyzer.summarytable import update_or_create_activity_summarytables

def update_or_create_summaryreports():
    update_or_create_summaryreport('A', 4)
    update_or_create_summaryreport('Q', 6)
    update_or_create_summaryreport('M', 6)
    update_or_create_summaryreport('W', 6)

def update_or_create_summaryreport(summary_type, no_of_columns):
    column_qs = get_summarytable_columns(summary_type, no_of_columns)
    most_recent_period = column_qs[0]
    report = SummaryReport(
        id=get_summaryreport_id(summary_type, most_recent_period),
        summary_type=summary_type,
        **most_recent_period  #most recent period gives the year etc.
        )
    report.save()
    columns = update_or_create_summarycolumns(report, column_qs)
    update_or_create_activity_summarytables(report, columns)

#
# -------------------------------------------------------------------
#
# Common summaryreport functions
#
# -------------------------------------------------------------------

def get_summaryreport_id(summary_type, entry):
    return "{}-{}".format(
        entry['year'],
        get_period_id(summary_type, entry)
        )

def get_full_period_id(summary_type, entry):
    if summary_type == 'A':
        return entry['year']
    else:
        return "{}-{}".format(
            entry['year'],
            get_period_id(summary_type, entry)
            )

def get_period_id(summary_type, entry):
    if summary_type == 'A':
        return 'A'
    elif summary_type =='Q':
        return 'Q{}'.format(entry['quarter'])
    elif summary_type == 'M':
        return 'M{}'.format(entry['month'])
    elif summary_type == 'W':
        return 'W{}'.format(entry['week'])

#
# -------------------------------------------------------------------
#
# Summarycolumn functions
#
# -------------------------------------------------------------------

def get_summarytable_columns(summary_type, no_of_columns):
    if summary_type == 'A':
        return ActivitySummary.objects.filter(summary_type=summary_type).values(
                'year', 'dt_start', 'dt_end').distinct().order_by(
                    '-dt_start')[:no_of_columns]
    elif summary_type =='Q':
        return ActivitySummary.objects.filter(summary_type=summary_type).values(
                'year', 'quarter', 'dt_start', 'dt_end').distinct().order_by(
                    '-dt_start')[:no_of_columns]
    elif summary_type == 'M':
        return ActivitySummary.objects.filter(summary_type=summary_type).values(
                'year', 'month', 'dt_start', 'dt_end').distinct().order_by(
                    '-dt_start')[:no_of_columns]
    elif summary_type == 'W':
        return ActivitySummary.objects.filter(summary_type=summary_type).values(
                'year', 'week', 'dt_start', 'dt_end').distinct().order_by(
                    '-dt_start')[:no_of_columns]

def update_or_create_summarycolumns(report, column_qs):
    columns = list()
    for item in enumerate(column_qs):
        column = SummaryColumn(
            id=get_columnid(report, item[0]),
            report=report,    
            column_number=item[0],
            dt_start=item[1]['dt_start'],
            dt_end=item[1]['dt_end'],
            period=get_full_period_id(report.summary_type, item[1])
            )
        column.save()
        columns.append(column)
    return columns

def get_columnid(report, column_number):
    return "{}-{}".format(report.id, column_number)

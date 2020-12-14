from StravaAnalyzer.models import Athlete, ActivitySummary, SummaryTable, SummaryRow, SummaryCell, SummaryTotal, ColumnTotal
from django.db.models import Count, Sum, Avg

def update_or_create_activity_summarytables(report, columns):
    dt_earliest = columns[-1].dt_start
    sport_types_w_totals = get_ordered_list_of_sport_types(
                                report.summary_type, dt_earliest)
    for sport_type_w_total in sport_types_w_totals:
        table = update_or_create_activity_summarytable(
                    report, sport_type_w_total, columns)

def update_or_create_activity_summarytable(report, sport_type_w_total, columns):
    table = SummaryTable(
        id=get_summarytable_id(report.id, sport_type_w_total['sport_type']),
        report=report,
        **sport_type_w_total
        )
    table.save()
    update_or_create_activity_summaryrows(table, columns)
    update_or_create_summary_columntotals(table, columns)
    return table

def get_ordered_list_of_sport_types(summary_type, dt_earliest):
    return ActivitySummary.objects.filter(
            summary_type=summary_type, 
            dt_start__gte=dt_earliest
            ).values('sport_type').annotate(
                    total_elapsed_time=Sum('sum_elapsed_time')
                    ).order_by('-total_elapsed_time')

def get_summarytable_id(report_id, sport_type):
    return "{}-{}".format(report_id, sport_type)

#
# -------------------------------------------------------------------
#
# Summaryrow functions
#
# -------------------------------------------------------------------

def update_or_create_activity_summaryrows(table, columns):
    stats = get_ordered_list_of_athlete_stats(table, columns)
    for stat in stats:
        update_or_create_activity_summaryrow(table, stat, columns)

def update_or_create_activity_summaryrow(table, stat, columns):
    athlete = Athlete.objects.get(id=stat['athlete'])
    del stat['athlete'] # to use "stat" in creating the SummaryRow object
    row = SummaryRow(
        id=get_summaryrow_id(table.id, athlete.id),
        summarytable=table,
        athlete=athlete,
        **stat
        )
    row.save()
    update_or_create_summarycells(row, columns)

def get_ordered_list_of_athlete_stats(table, columns):
        dt_earliest = columns[-1].dt_start

        return ActivitySummary.objects.filter(
            summary_type=table.report.summary_type,
            dt_start__gte=dt_earliest,
            sport_type=table.sport_type
            ).values('athlete').annotate(
                total_activity_count=Sum('activity_count'),
                total_elapsed_time=Sum('sum_elapsed_time'),
                total_distance=Sum('sum_distance')
                ).order_by('-total_elapsed_time')

def get_summaryrow_id(table_id, athlete_id):
    return "{}-{}".format(table_id, athlete_id)

#
# -------------------------------------------------------------------
#
# Summarycell functions
#
# -------------------------------------------------------------------

def update_or_create_summarycells(row, columns):
    summaries = get_athlete_summaries_for_row(row, columns)
    for column in columns:
        summary = [s for s in summaries 
                    if s.dt_start == column.dt_start]
        # summary can be an empty list, but the function accommodates that
        update_or_create_activity_summarycell(summary, row, column)

def update_or_create_activity_summarycell(summary, row, column):
    cell = SummaryCell(
        id=get_summarycell_id(row.id, column.column_number),
        summaryrow=row,
        column_number=column.column_number,
        dt_start = column.dt_start,
        dt_end = column.dt_end
        )
    if summary: # in the list comprehension
                # a matching ActivitySummary is found or not.
        cell.activity_count = summary[0].activity_count
        cell.sum_elapsed_time = summary[0].sum_elapsed_time
        cell.sum_distance = summary[0].sum_distance
        cell.rank_time = summary[0].rank_time
        cell.rank_distance = summary[0].rank_distance
    else:
        cell.activity_count = 0
        cell.sum_elapsed_time = 0
        cell.sum_distance = 0
        cell.rank_time = None
        cell.rank_distance = None
    cell.save()

def get_athlete_summaries_for_row(row, columns):
        dt_earliest = columns[-1].dt_start

        return ActivitySummary.objects.filter(
            summary_type=row.summarytable.report.summary_type,
            dt_start__gte=dt_earliest,
            sport_type=row.summarytable.sport_type,
            athlete=row.athlete).order_by('-dt_start')

def get_summarycell_id(row_id, column_number):
    return "{}-{}".format(row_id, column_number)

#
# -------------------------------------------------------------------
#
# ColumnTotal functions
#
# -------------------------------------------------------------------

def update_or_create_summary_columntotals(table, columns):
    summarytotals = get_summarytotals_for_table(table, columns)
    for column in columns:
        summarytotal = [s for s in summarytotals
                    if s.dt_start == column.dt_start]
        # summarytotal can be an empty list, which is fine for the function
        update_or_create_columntotal(summarytotal, table, column)

def update_or_create_columntotal(summarytotal, table, column):
    columntotal = ColumnTotal(
        id=get_columntotal_id(table.id, column.column_number),
        summarytable=table,
        column=column
        )
    if summarytotal: # in the list comprehension
                     # a matching SummaryTotal is found or not.
        columntotal.avg_activity_count = summarytotal[0].avg_activity_count
        columntotal.avg_elapsed_time = summarytotal[0].avg_elapsed_time
        columntotal.avg_distance = summarytotal[0].avg_distance
    else:
        columntotal.avg_activity_count = None
        columntotal.avg_elapsed_time = None
        columntotal.avg_distance = None
    columntotal.save()

def get_summarytotals_for_table(table, columns):
        dt_earliest = columns[-1].dt_start

        return SummaryTotal.objects.filter(
            summary_type=table.report.summary_type,
            dt_start__gte=dt_earliest,
            sport_type=table.sport_type
            ).order_by('-dt_start')

def get_columntotal_id(table_id, column_number):
    return "{}-{}".format(table_id, column_number)
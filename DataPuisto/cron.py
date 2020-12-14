#
# -------------------------------------------------------------------
#
# The key daily Cron function calls
#
# -------------------------------------------------------------------

from StravaAnalyzer.fetch import fetch_all_activities
from StravaAnalyzer.activitysummary import update_or_create_activity_summaries
from StravaAnalyzer.summaryreport import update_or_create_summaryreports

fetch_all_activities()
update_or_create_activity_summaries()
update_or_create_summaryreports()


#
# -------------------------------------------------------------------
#
# Launching PuistoMan updates (NavigantAnalyzer v. 2.0, 2019-12-05)
#
# -------------------------------------------------------------------

from NavigantAnalyzer.initializers import puistoserie_init_values, pointsschema_assign_values
from NavigantAnalyzer.initializers import for_all_obj_do_puistoman_updates

puistoserie_init_values()
pointsschema_assign_values()
for_all_obj_do_puistoman_updates()

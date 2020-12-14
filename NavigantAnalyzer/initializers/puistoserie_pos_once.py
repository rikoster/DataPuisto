from NavigantAnalyzer.models import Puistoserie, Puistoseriescore

#
# The module added by Riku on 2020-10-18 to calculate once the new
# Puistoseriescore position field added on 2020-10-18 to existing data.
#

def update_ps_positions(ps_obj):
    # This function relies on the defined ordering of Puistoseriescores
    pss_qs = ps_obj.puistoseriescore_set.all()
    score_list = [pss_obj.score for pss_obj in pss_qs]
    for pss_obj in pss_qs:
        # list.index gives the first occurrence in the list
        pss_obj.position = score_list.index(pss_obj.score) + 1
        pss_obj.save()    

def update_ps_positions_for_all_obj():
    for ps_obj in Puistoserie.objects.all():
        update_ps_positions(ps_obj)

update_ps_positions_for_all_obj()

from django.db import models
from NavigantAnalyzer.common import convert_datetime_string
import json

# A custom view-based model for flat outputs - RÖ - 2018-10-24
# Don't add, change or delete fields without editing the view in the Db
class Results_flat(models.Model):
    race_id = models.IntegerField()
    race_name = models.CharField(max_length=127)
    race_serie = models.CharField(max_length=127, blank=True)
    race_begin = models.DateTimeField(blank=True, null=True)
    result_start_time = models.DateTimeField(blank=True, null=True)
    runner_last_name = models.CharField(max_length=63, blank=True)
    runner_first_name = models.CharField(max_length=63, blank=True)
    result_emit = models.CharField(max_length=12, blank=True)
    course_name = models.CharField(max_length=63)
    course_length = models.IntegerField(blank=True, null=True)
    course_num_participants = models.IntegerField(blank=True, null=True)
    course_min_time = models.IntegerField(blank=True, null=True)
    course_mean_time = models.IntegerField(blank=True, null=True)
    course_min_puistotime = models.IntegerField(blank=True, null=True)
    course_mean_puistotime = models.IntegerField(blank=True, null=True)
    visit_min_time = models.IntegerField(blank=True, null=True)
    visit_mean_time = models.IntegerField(blank=True, null=True)
    visit_min_puistotime = models.IntegerField(blank=True, null=True)
    visit_mean_puistotime = models.IntegerField(blank=True, null=True)
    visit_puistoman_time = models.IntegerField(blank=True, null=True) # Since 2019-12-08
    leg_min_time = models.IntegerField(blank=True, null=True)
    leg_mean_time = models.IntegerField(blank=True, null=True)
    leg_min_puistotime = models.IntegerField(blank=True, null=True)
    leg_mean_puistotime = models.IntegerField(blank=True, null=True)
    visit_order = models.IntegerField()
    visit_code = models.IntegerField()
    visit_time = models.IntegerField()
    visit_position = models.IntegerField(blank=True)
    visit_puistoposition = models.IntegerField(blank=True)
    leg_time = models.IntegerField(blank=True)
    leg_position = models.IntegerField(blank=True)
    leg_puistoposition = models.IntegerField(blank=True)
    visit_puistodiff_time_l = models.IntegerField(blank=True, null=True) # Since 2019-12-08
    visit_puistodiff_time_pm = models.IntegerField(blank=True, null=True) # Since 2019-12-08
    leg_puistodiff_time_l = models.IntegerField(blank=True, null=True) # Since 2019-12-08
    leg_puistodiff_time_pm = models.IntegerField(blank=True, null=True) # Since 2019-12-08
    leg_puistoperc_time_l = models.FloatField(null=True) # Since 2019-12-08
    leg_puistoperc_time_pm = models.FloatField(null=True) # Since 2019-12-08
    leg_puistoperc_time_l = models.FloatField(null=True) # Since 2019-12-08
    leg_puisto_success = models.FloatField(null=True) # Since 2019-12-08
    result_puistoperc_time_l = models.FloatField(null=True) # Since 2019-12-08
    result_puistoperc_time_pm = models.FloatField(null=True) # Since 2019-12-08
    result_puisto_max_level = models.FloatField(null=True) # Since 2019-12-08
    result_puisto_success = models.FloatField(null=True) # Since 2019-12-08
    result_puisto_optimum = models.IntegerField(null=True) # Since 2019-12-08
    result_puisto_mistakes = models.IntegerField(null=True) # Since 2019-12-08

    class Meta:
        managed = False
        db_table = 'NavigantAnalyzer_results_flat'

    def get_fields(self):
        result = dict()
        datetime_fields = ['race_begin', 'result_start_time']
        for field in Results_flat._meta.fields:
            value = field.value_to_string(self)
            if value.isdigit():
                value = int(value)
            if field.name in datetime_fields:
                value = convert_datetime_string(value)
            result[field.name] = value
        return json.dumps(result)

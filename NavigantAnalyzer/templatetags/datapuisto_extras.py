from datetime import timedelta
from django import template
from NavigantAnalyzer.models import Race, Puistoserie

register = template.Library()

@register.filter(is_safe=True)
def time_string(value):
    try:
        time_seconds = int(value)
        sign = "" if time_seconds >= 0 else "-"
        mins, secs = divmod(abs(time_seconds), 60)
        if mins >= 60:
            hours, mins = divmod(mins, 60)
            return "{}{}:{:02d}:{:02d}".format(sign, hours, mins, secs)
        else:
            return "{}{}:{:02d}".format(sign, mins, secs)
    except:
        return ""

@register.filter(is_safe=True)
def perc_string(value):
    try:
        mega = int(value*1000000) + 500 #500 needed for proper rounding
        perc, d = divmod(mega, 10000)
        return "{},{}%".format(perc, d//1000)
    except:
        return ""

@register.filter(is_safe=True)
def in_km(value):
    try:
        metres = int(value) + 50  #50 needed for proper rounding
        km, m = divmod(metres, 1000)
        return "{},{} km".format(km, m//100)
    except:
        return ""


@register.filter(is_safe=True)
def iitem(object_set, index):
    try:
        return object_set[index]
    except:
        return None

@register.filter(is_safe=True)
def iattr(object_set, attrname):
    try:
        return getattr(object_set, attrname)
    except:
        return None

@register.simple_tag
def race_latest_year():
    return Race.objects.filter(begin__isnull=False).latest('begin').begin.year

@register.simple_tag
def puistoserie_latest():
    return Puistoserie.objects.last().id

#def display_recent_races(no_of_races, order='-begin'):
#    full_html = '<table class="race">'
#    races = Race.objects.all().order_by(order)[:no_of_races]
#    for race in races:
#        full_html += race.display_html_row()
#    full_html += '</table>'
#    return full_html
        
#def get_race_html(input_id):
#    race = Race.objects.get(id=input_id)
#    return race.get_html


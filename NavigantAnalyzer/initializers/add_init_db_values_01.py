from NavigantAnalyzer.models import Club, Runner, MatchName

def add_init_db_values():
    c = Club(name="OC Puisto")
    c.save()

    o = Runner(first_name="Reima", last_name="Harju", name="Reima Harju")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Reima Harju")
    mn.save()
    mn=MatchName(runner=o, name="Harju Reima")
    mn.save()

    o = Runner(first_name="Markku", last_name="Helin", name="Markku Helin")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Markku Helin")
    mn.save()
    mn=MatchName(runner=o, name="Helin Markku")
    mn.save()

    o = Runner(first_name="Petri", last_name="Ketola", name="Petri Ketola")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Petri Ketola")
    mn.save()
    mn=MatchName(runner=o, name="Ketola Petri")
    mn.save()

    o = Runner(first_name="Uki", last_name="Lammi", name="Uki Lammi")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Uki Lammi")
    mn.save()
    mn=MatchName(runner=o, name="Lammi Uki")
    mn.save()

    o = Runner(first_name="Timo", last_name="Lappi", name="Timo Lappi")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Timo Lappi")
    mn.save()
    mn=MatchName(runner=o, name="Lappi Timo")
    mn.save()

    o = Runner(first_name="Mika", last_name="Martikainen", name="Mika Martikainen")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Mika Martikainen")
    mn.save()
    mn=MatchName(runner=o, name="Martikainen Mika")
    mn.save()

    o = Runner(first_name="Juha", last_name="Meronen", name="Juha Meronen")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Juha Meronen")
    mn.save()
    mn=MatchName(runner=o, name="Meronen Juha")
    mn.save()

    o = Runner(first_name="Mikko", last_name="Patrakka", name="Mikko Patrakka")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Mikko Patrakka")
    mn.save()
    mn=MatchName(runner=o, name="Patrakka Mikko")
    mn.save()

    o = Runner(first_name="Mark", last_name="Roth", name="Mark Roth")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Mark Roth")
    mn.save()
    mn=MatchName(runner=o, name="Roth Mark")
    mn.save()

    o = Runner(first_name="Jari", last_name="Siitonen", name="Jari Siitonen")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Jari Siitonen")
    mn.save()
    mn=MatchName(runner=o, name="Siitonen Jari")
    mn.save()

    o = Runner(first_name="Eerik", last_name="Skyttä", name="Eerik Skyttä")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Eerik Skyttä")
    mn.save()
    mn=MatchName(runner=o, name="Skyttä Eerik")
    mn.save()

    o = Runner(first_name="Henrik", last_name="Skyttä", name="Henrik Skyttä")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Henrik Skyttä")
    mn.save()
    mn=MatchName(runner=o, name="Skyttä Henrik")
    mn.save()

    o = Runner(first_name="Ville", last_name="Säde", name="Ville Säde")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Ville Säde")
    mn.save()
    mn=MatchName(runner=o, name="Säde Ville")
    mn.save()

    o = Runner(first_name="Kalle", last_name="Turkkila", name="Kalle Turkkila")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Kalle Turkkila")
    mn.save()
    mn=MatchName(runner=o, name="Turkkila Kalle")
    mn.save()

    o = Runner(first_name="Riku", last_name="Österman", name="Riku Österman")
    o.save()
    o.clubs.add(c)

    mn=MatchName(runner=o, name="Riku Österman")
    mn.save()
    mn=MatchName(runner=o, name="Österman Riku")
    mn.save()

from NavigantAnalyzer.models import Puistoserie, Pointsschema

def puistoserie_init_values():
    ps = Puistoserie(name="Helsinki Night Challenge syksy 2018")
    ps.save()
    ps = Puistoserie(name="Helsinki Night Challenge kevät 2019")
    ps.save()
    ps = Puistoserie(name="Helsinki Night Challenge syksy 2019")
    ps.save()

def pointsschema_assign_values():
    ps = Pointsschema(position=1, points=25)
    ps.save()
    ps = Pointsschema(position=2, points=18)
    ps.save()
    ps = Pointsschema(position=3, points=15)
    ps.save()
    ps = Pointsschema(position=4, points=12)
    ps.save()
    ps = Pointsschema(position=5, points=10)
    ps.save()
    ps = Pointsschema(position=6, points=8)
    ps.save()
    ps = Pointsschema(position=7, points=6)
    ps.save()
    ps = Pointsschema(position=8, points=4)
    ps.save()
    ps = Pointsschema(position=9, points=2)
    ps.save()
    ps = Pointsschema(position=10, points=1)
    ps.save()
    ps = Pointsschema(position=11, points=0)
    ps.save()
    ps = Pointsschema(position=12, points=0)
    ps.save()
    ps = Pointsschema(position=13, points=0)
    ps.save()
    ps = Pointsschema(position=14, points=0)
    ps.save()
    ps = Pointsschema(position=15, points=0)
    ps.save()
    ps = Pointsschema(position=16, points=0)
    ps.save()
    ps = Pointsschema(position=17, points=0)
    ps.save()
    ps = Pointsschema(position=18, points=0)
    ps.save()
    ps = Pointsschema(position=19, points=0)
    ps.save()
    ps = Pointsschema(position=20, points=0)
    ps.save()
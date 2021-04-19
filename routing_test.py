import sketch

from phidl import Port
routing=sketch.Routing(name="Route")

routing.clearance=((0,0),(500,500))

routing.ports=[Port(name='1',midpoint=(200,-100),width=50,orientation=90),\
    Port(name='2',midpoint=(300,600),width=50,orientation=90)]

# routing.test()

sketch.check_cell(routing.draw_with_frame())

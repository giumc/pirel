import sketch

from phidl import Port
routing=sketch.Routing("Route")

routing.clearance=((0,0),(500,500))

routing.ports=[Port(name='1',midpoint=(-100,-100),width=50,orientation=0),\
    Port(name='2',midpoint=(600,300),width=50,orientation=180)]

sketch.check_cell(routing.draw_frame())

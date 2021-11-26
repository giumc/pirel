import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps

import traceback

bbox=((0,100),(400,600))

route=pc.Routing()

route.source=dl.Port(
    name='source',
    midpoint=(-100,0),
    width=50,
    orientation=90)

route.destination=dl.Port(
    name='destination',
    midpoint=(200,800),
    width=50,
    orientation=90)

route.trace_width=20

route.clearance=bbox

cell=pg.bbox(bbox)
# pt.check(route._draw_frame())

cell<<route.draw()

pt.check(cell)

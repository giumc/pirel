import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps

bbox=((0,100),(400,600))

route=pc.Routing()

route.source=dl.Port(
    name='source',
    midpoint=(0,0),
    orientation=90)

route.destination=dl.Port(
    name='destination',
    midpoint=(200,0),
    orientation=90)

route.trace_width=20

route.clearance=bbox

cell=pg.bbox(bbox)

cell<<route.draw()

pt.check(cell)

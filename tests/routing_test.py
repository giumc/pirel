import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.sketch_tools as st
import pirel.addOns.standard_parts as ps

import traceback

bbox=((0,100),(400,600))

route=pc.Routing()

route.source=dl.Port(
    name='source',
    midpoint=(200,0),
    width=50,
    orientation=90)

route.destination=dl.Port(
    name='destination',
    midpoint=(200,800),
    width=50,
    orientation=0)

route.trace_width=20

route.clearance=bbox

route.overhang=50

route.side='right'

cell=pg.bbox(bbox)
# st.check(route._draw_frame())
cell<<route.draw()

st.check(cell)

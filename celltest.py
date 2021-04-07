import LayoutClasses as lc
import os
import numpy as np

import phidl.geometry as pg

from phidl import quickplot as qp

import gdspy
#
idt=lc.IDT(name="hello")
#
cell=idt.draw()

lib=gdspy.GdsLibrary("cell")

lib.add(cell)

gdspy.LayoutViewer(lib)

# r=pg.ring()
#
# idt=lc.IDT(name='IDT')
# cell=idt.draw()

# bus=lc.Bus(name='buss')
#
# bus.size=lc.Point(20,30)
# bus.distance=lc.Point(28,0)
# bus.origin=lc.Point(-5,0)
# cell=bus.draw()
#
# o=lc.Point(0,0)
#
# r_size=lc.Point(20,30)
#
# e_width=5
#
# etch=lc.EtchPit(name='pitt')
#
# cell_box=gdspy.Cell('boxcell')
#
# box=gdspy.Rectangle(o.get_coord(),r_size.get_coord(),layer=1)
#
# cell_box.add(box)
#
# etch.x=e_width
#
# etch.active_area=lc.LayoutTool().get_size(cell_box)
#
# etch.etch_margin=lc.Point(1,1)
#
# etch.origin=lc.Point(-etch.x-etch.etch_margin.x,-etch.etch_margin.y)
#
# etch.anchor_etch=True
#
# etch.anchor_etch_size=lc.Point(10,10)
#
# cell=etch.draw()
#
# cell.add(cell_box)

# res=lc.BaseLFEResonator(name='ress')

# pit=lc.EtchPit()

# res.etchpit.anchor_etch=True

# res.anchor.size=lc.Point(40,20)
#
# res.etchpit.etch_margin.y=2
#
# res.etchpit.x=40
#
# cell=res.draw()
#
# probe=lc.GSProbe(name='probe')
#
# # cell.add(probe.draw())
#
# res_marker_lines=res.get_anchor_lines()
#
# probe.bottom_marker=res_marker_lines[0]
#
# probe.top_marker=res_marker_lines[1]
#
# cell=lc.LayoutTool().merge_cells(cell,probe.draw())
# # busline=res.etchpit.get_anchor_lines()
#
# # cell.add(gdspy.Rectangle((busline[0].p1-lc.Point(0,20)).get_coord(),\
#     # (busline[0].p2).get_coord()))
#
# lib.add(cell)
#
# outname=lib.name+'.gds'
#
# if os.path.exists(outname):
#
#     os.remove(outname)
#
# # lib.write_gds(outname)
# # gdspy.GdsWriter(lib.name+'.gds')
# gdspy.LayoutViewer(lib)

import sketch

# import phidl.geometry as pg

import gdspy

from phidl import quickplot as qp

import matplotlib.pyplot as plt

# idt=sketch.IDT("hey").test()

# pit=sketch.EtchPit("pitt").test()

# anchor=sketch.Anchor("an").test()

# res=sketch.LFERes('ress').test()

# res=sketch.FBERes('ress').test()

# via=sketch.Via('viass').test()

# gsg=sketch.GSGProbe("probs").test()

# gs=sketch.GSProbe("probs").test()

# tfe=sketch.TFERes("hi")
# tfe.draw()
# tfe.add_text(location='bottom')
# tfe.add_text(location='top')
# sketch.check_cell(tfe.cell)

# r=sketch.Routing(side='left')
#
# frame=r.draw_frame()
# routing=r.draw()
# routing<<frame
# sketch.check_cell(routing)

d=sketch.DUT("hi")
d.dut.idt.n=4
d.dut.anchor.etch_choice=False
d.routing_width=80
d.test()

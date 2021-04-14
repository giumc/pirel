import sketch

# import phidl.geometry as pg

import gdspy

from phidl import quickplot as qp

import matplotlib.pyplot as plt

# idt=sketch.IDT("hey").test()

# pit=sketch.EtchPit("pitt").test()

# anchor=sketch.Anchor("an").test()

# res=sketch.LFERes('ress')
# res.test()
# print(res.get_data_table().to_string())

# res=sketch.FBERes('ress').test()

# via=sketchB.Via('viass').test()

# gsgB=sketch.GSGProbe("probs").test()

# gs=sketch.GSProbe("probs").test()

tfe=sketch.TFERes("hi").test()
# print(tfe.get_data_table().to_string())
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

# sketch.GSGProbe_LargePad().test()
# d=sketch.DUT("hi")
# d.dut.idt.n=8
# d.dut.anchor.etch_choice=False
# d.routing_width=120
# d.test()

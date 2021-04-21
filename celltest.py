
# import phidl.geometry as pg
import sketch

import gdspy

from phidl import quickplot as qp

import matplotlib.pyplot as plt

# idt=sketch.IDT("hey")
#
# idt.view()

# pit=sketch.EtchPit("pitt").view()

# anchor=sketch.Anchor("an").view()

# res=sketch.LFERes('ress')
# res.view()
# print(res.export_params().to_string())

# res=sketch.FBERes('ress').view()

# via=sketchB.Via('viass').view()

# gsgB=sketch.GSGProbe("probs").view()

# gs=sketch.GSProbe("probs").view()

tfe=sketch.LFERes_wVia("bu")
tfe.overvia=4
tfe.via.type='rectangle'
# tfe.via.size=50
tfe.view()

# print(tfe.export_params().to_string())

# df=tfe.export_params()
# print(df)
# df["IDTPitch"]=50

# print(*df.columns.values,sep='\n')

# tfe.import_params(df)

# tfe.view()
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

# sketch.GSGProbe_LargePad().view()
#
d=sketch.DUT("hi")
# # d.dut.anchor.etch_choice=False
d.dut=tfe
d.dut.idt.n=20
d.routing_width=100
d.probe.size=sketch.Point(50,50)
d.probe.groundsize=300
# # # import pdb; pdb.set_trace()
print(d)
d.view()
# df["IDTN_fingers"]=3
# # # df["BusSize"]=sketch.Point(50,200)
# # df["AnchorSize"]=sketch.Point(300,50)
# # df["AnchorEtchMargin"]=sketch.Point(5,10)
# d.import_params(df)
# d.view()
#
# dut=d.dut
#
# dut.view()
#
# df=dut.export_params()
# df["BusSize"]=sketch.Point(100,400)
# df=dut.import_params(df)
# anchor=dut.view()
# print(*df.columns.values,sep='\n')
# print(d.export_params().to_string())

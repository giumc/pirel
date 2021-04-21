
# import phidl.geometry as pg
import sketch

import gdspy

from phidl import quickplot as qp

import matplotlib.pyplot as plt

# idt=sketch.IDT("hey")
#
# idt.test()

# pit=sketch.EtchPit("pitt").test()

# anchor=sketch.Anchor("an").test()

# res=sketch.LFERes('ress')
# res.test()
# print(res.export_params().to_string())

# res=sketch.FBERes('ress').test()

# via=sketchB.Via('viass').test()

# gsgB=sketch.GSGProbe("probs").test()

# gs=sketch.GSProbe("probs").test()

tfe=sketch.LFERes_wVia("bu")
tfe.overvia=2
tfe.via.size=50
tfe.test()

# print(tfe.export_params().to_string())

# df=tfe.export_params()
# print(df)
# df["IDTPitch"]=50

# print(*df.columns.values,sep='\n')

# tfe.import_params(df)

# tfe.test()
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
#
# d=sketch.DUT("hi")
# # d.dut.anchor.etch_choice=False
# d.dut.idt.n=20
# d.routing_width=100
# d.probe.size=sketch.Point(50,50)
# d.probe.groundsize=300
# # # import pdb; pdb.set_trace()
# df=d.export_params()
# d.test()
# df["IDTN_fingers"]=3
# # # df["BusSize"]=sketch.Point(50,200)
# # df["AnchorSize"]=sketch.Point(300,50)
# # df["AnchorEtchMargin"]=sketch.Point(5,10)
# d.import_params(df)
# d.test()
#
# dut=d.dut
#
# dut.test()
#
# df=dut.export_params()
# df["BusSize"]=sketch.Point(100,400)
# df=dut.import_params(df)
# anchor=dut.test()
# print(*df.columns.values,sep='\n')
# print(d.export_params().to_string())

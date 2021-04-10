import sketch

import phidl.geometry as pg

import gdspy

from phidl import quickplot as qp

import matplotlib.pyplot as plt

# def test(self):
#
#     qp(self.draw())
#     plt.pause(100)

# idt=sketch.IDT("hey").test()

# bus=sketch.Bus("hey")
# test(bus)

# pit=sketch.EtchPit("pitt")
# pit.anchor_etch=False
# test(pit)

# anchor=sketch.Anchor("an")
# test(anchor)

# res=sketch.LFERes('ress')
# res.anchor.x_offset=0
# res.anchor.size=sketch.Point(40,20)
# res.idt.n=20
# res.etchpit.x=60
# res.anchor.size=sketch.Point(8,8)
# res.anchor.x_offset=0
# res.test()

res=sketch.FBERes('ress').test()

# via=sketch.Via('viass')
# via.type='circle'
# via.test()

# gsg=sketch.GSGProbe("probs")
# gsg.size=sketch.Point(80,80)
# gsg.pitch=100
# gsg.test()

# gs=sketch.GSProbe("probs")
# gs.size=sketch.Point(80,80)
# gs.pitch=100
# gs.test()

# tfe=sketch.TFERes("hi").test()

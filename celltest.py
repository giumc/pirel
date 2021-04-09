import LayoutClasses as lc

import phidl.geometry as pg

import gdspy

from phidl import quickplot as qp

import matplotlib.pyplot as plt

# def test(self):
#
#     qp(self.draw())
#     plt.pause(100)

# idt=lc.IDT("hey")
# test(idt)

# bus=lc.Bus("hey")
# test(bus)

# pit=lc.EtchPit("pitt")
# pit.anchor_etch=False
# test(pit)

# anchor=lc.Anchor("an")
# test(anchor)

res=lc.LFERes('ress')
res.anchor.x_offset=0
res.anchor.size=lc.Point(40,20)
res.idt.n=40
res.etchpit.x=60
res.test_gds()

# res=lc.FBERes('ress').test()

# via=lc.Via('viass')
# via.type='circle'
# via.test()

# gsg=lc.GSGProbe("probs")
# gsg.test()

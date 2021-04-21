
import sketch

import gdspy

from phidl import quickplot as qp

import matplotlib.pyplot as plt

# idt=sketch.IDT("hey")
#
# idt.view()

# pit=sketch.EtchPit("pitt").view()

# anchor=sketch.Anchor("an").view()
#
lfe=sketch.LFERes('ress')

lfe.view()
# sketch.FBERes('ress').view()
#
# sketch.TFERes("bu").view()
#
#
# tfe.overvia=4
#
# tfe.via.type='rectangle'
#
# tfe.view()

# print(tfe.export_params().to_string())

d=sketch.DUT("hi")

d.dut=sketch.Scaled(sketch.LFERes)()

base_params=d.dut.export_params()

base_params["ProbeWidth"]=100
base_params["ProbePitch"]=200
base_params["ProbeLength"]=100
base_params["RoutingWidth"]=250
base_params["IDTPitch"]=7
base_params["IDTN_fingers"]=38
base_params["IDTOffset"]=1
base_params["IDTLength"]=105
base_params["IDTCoverage"]=0.5
base_params["BusLength"]=4
base_params["EtchWidth"]=0.4
base_params["AnchorLength"]=4
base_params["AnchorWidth"]=0.5
base_params["AnchorEtchMarginX"]=0.5
base_params["AnchorEtchMarginY"]=0.5
base_params["ProbeGroundPadSize"]=200

d.dut.import_params(base_params)

d.view()

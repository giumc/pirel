
import sketch

import gdspy

from phidl import quickplot as qp

import matplotlib.pyplot as plt

import pandas as pd
# idt=sketch.IDT("hey")
#
# idt.view()

# pit=sketch.EtchPit("pitt").view()

# anchor=sketch.Anchor("an").view()
#
# lfe=sketch.LFERes('ress')

# lfe.view()

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

# d=sketch.DUT("hi")
#
# d.dut=sketch.Scaled(sketch.addVia(sketch.LFERes))()
#
# print(d.dut.__class__.__name__)
# d.probe=sketch.GSGProbe()

# d.dut.print_params_name()
# print(d.dut.__class__.__name__)
# base_params=d.export_params()
#
# d.print_params_name()
#
# base_params["ProbeWidth"]=100
# base_params["ProbePitch"]=200
# base_params["ProbeLength"]=100
# base_params["RoutingWidth"]=250
# base_params["IDTPitch"]=7
# base_params["IDTN_fingers"]=38
# base_params["IDTOffset"]=1
# base_params["IDTLength"]=105
# base_params["IDTCoverage"]=0.5
# base_params["BusLength"]=4
# base_params["EtchWidth"]=0.4
# base_params["AnchorLength"]=4
# base_params["AnchorWidth"]=0.5
# base_params["AnchorEtchMarginX"]=0.5
# base_params["AnchorEtchMarginY"]=0.5
# base_params["ViaSize"]=30
# base_params["Overvia"]=3
#
# d.import_params(base_params)
#
# d.view()
#
# d=sketch.Pad("hi")
#
# d.view()

# d=sketch.addVia(sketch.TFERes)()

# d.view()

d=sketch.Stack("hey")

d.device=sketch.addVia(sketch.TFERes)("hey")
d.device.overvia=3
d.device.via.size=30
# d.import_params(pd.DataFrame({"PadSize":150},index=[0]))
d.view()

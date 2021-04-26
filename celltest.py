from sketch import *

import gdspy

from phidl import quickplot as qp

import pandas as pd

d=addProbe(\
    addVia(array(Scaled(LFERes),8)),\
    addLargeGnd(GSGProbe))(name="DEF")

base_params=d.export_params()

base_params["ProbeGroundPadSize"]=400
base_params["ProbeWidth"]=100
base_params["ProbePitch"]=200
base_params["ProbeLength"]=100
base_params["ProbeDistance"]=150
base_params["GNDRoutingWidth"]=100

base_params["IDTPitch"]=7
base_params["IDTN_fingers"]=4
base_params["IDTOffset"]=1
base_params["IDTLength"]=105
base_params["IDTCoverage"]=0.5
base_params["BusLength"]=0.5
base_params["EtchWidth"]=0.4
base_params["AnchorLength"]=4
base_params["AnchorWidth"]=0.5
base_params["AnchorEtchMarginX"]=0.45
base_params["AnchorEtchMarginY"]=0.2

base_params["ExtConnLength"]=10

base_params["ViaSize"]=40
base_params["ViaAreaX"]=300
base_params["ViaAreaY"]=300
base_params["ViaShape"]='rectangle'
base_params["Overvia"]=2

d.import_params(base_params)

d._stretch_top_margin=True

d.view()
print(d.resistance())
# p=PArraySeries(d)

# p.x_param=[\
# SweepParam({'IDTN_fingers':[5,10,15,20]}),\
# SweepParam({'IDTLength':[20,40,60]})]
# SweepParam({'ViaSize':[10,20,50]})]

# p.view()
# rpq=1

# print(d.resistance(res_per_square=rpq))

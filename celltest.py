from sketch import *

import gdspy

from phidl import quickplot as qp

import pandas as pd

d=addProbe(addVia(Scaled(LFERes)),addLargeGnd(GSGProbe)())(name="DEF")

base_params=d.export_params()

base_params["EtchWidth"]=0.5
base_params["AnchorWidth"]=0.3
base_params["AnchorLength"]=5
base_params["AnchorEtchMarginX"]=2
base_params["AnchorEtchMarginY"]=0.5
base_params["BusLength"]=1
base_params["IDTOffset"]=1
base_params["IDTN_fingers"]=20
base_params["IDTLength"]=40
base_params["ViaSize"]=50
base_params["ViaShape"]='rectangle'
base_params["Overvia"]=2
base_params["ViaSize"]=40
base_params["Overvia"]=2
base_params["IDTLength"]=20
base_params["IDTN_fingers"]=10
base_params["PadSize"]=50
base_params["SignalRoutingWidth"]=10
base_params["GndRoutingWidth"]=200
base_params["DutProbeDistance"]=100
base_params["ViaDistance"]=100
base_params["ViaAreaX"]=200
base_params["ViaAreaY"]=200

d.import_params(base_params)

# help(d)

p=PArraySeries(d)

p.x_param=[\
SweepParam({'IDTN_fingers':[5,10,15,20]}),\
SweepParam({'IDTLength':[20,40,60]}),\
SweepParam({'ViaSize':[10,20,50]})]

p.view()
# rpq=1

# print(d.resistance(res_per_square=rpq))

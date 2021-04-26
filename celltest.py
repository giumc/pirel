from sketch import *

import gdspy

from phidl import quickplot as qp

import pandas as pd

d=addProbe(\
    array(Scaled(LFERes),3),\
    addLargeGnd(GSGProbe))(name="DEF")

base_params=d.export_params()

base_params["ProbeGroundPadSize"]=400
base_params["ProbeWidth"]=100
base_params["ProbePitch"]=200
base_params["ProbeLength"]=100
base_params["ProbeDistance"]=180
base_params["GNDRoutingWidth"]=350

base_params["IDTPitch"]=7
base_params["IDTN_fingers"]=38
base_params["IDTOffset"]=1
base_params["IDTLength"]=105
base_params["IDTCoverage"]=0.5
base_params["BusLength"]=1
base_params["EtchWidth"]=0.4
base_params["AnchorLength"]=4
base_params["AnchorWidth"]=0.5
base_params["AnchorEtchMarginX"]=0.4
base_params["AnchorEtchMarginY"]=0.5

base_params["ExtConnLength"]=3
# base_params["ViaSize"]=20
# base_params["ViaAreaX"]=200
# base_params["ViaAreaY"]=200
# base_params["ViaShape"]='rectangle'
# base_params["Overvia"]=3

d.import_params(base_params)

d.view()
exit()

# help(d)

p=PArraySeries(d)

p.x_param=[\
SweepParam({'IDTN_fingers':[5,10,15,20]}),\
SweepParam({'IDTLength':[20,40,60]}),\
SweepParam({'ViaSize':[10,20,50]})]

p.view()
# rpq=1

# print(d.resistance(res_per_square=rpq))

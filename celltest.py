from sketch import *

import gdspy

from phidl import quickplot as qp

import pandas as pd

d=addProbe(Scaled(LFERes),GSGProbe_LargePad())(name="DEF")

base_params=d.export_params()

base_params["EtchWidth"]=0.5
base_params["AnchorWidth"]=0.2
base_params["AnchorLength"]=5
base_params["AnchorEtchMarginX"]=2.5
base_params["AnchorEtchMarginY"]=0.5
base_params["BusLength"]=4
base_params["IDTOffset"]=1
base_params["ViaSize"]=50
base_params["ViaShape"]='rectangle'
base_params["Overvia"]=2
base_params["ViaSize"]=50
base_params["Overvia"]=2
base_params["IDTLength"]=20
base_params["IDTN_fingers"]=10
base_params["PadSize"]=50
base_params["SignalRoutingWidth"]=10

print(d.resistance(res_per_square=1))

d.import_params(base_params)

d.view()

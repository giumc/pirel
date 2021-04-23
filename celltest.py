from sketch import *

import gdspy

from phidl import quickplot as qp

import pandas as pd

d=Sketch(Scaled(LFERes))(name="DEF")

base_params=d.export_params()

base_params["EtchWidth"]=0.5
base_params["AnchorWidth"]=0.5
base_params["AnchorLength"]=5
base_params["AnchorEtchMarginX"]=0.5
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

d.import_params(base_params)

d.view()

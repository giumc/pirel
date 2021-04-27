from sketch import *
from standard import *
import gdspy

from phidl import quickplot as qp

import pandas as pd

# d=addProbe(\
#     addVia(array(Scaled(FBERes),1)),\
#     addLargeGnd(GSGProbe))(name="DEF")
#
# base_params=d.export_params()
#
# base_params["ProbeGroundPadSize"]=400
# base_params["ProbeWidth"]=100
# base_params["ProbePitch"]=200
# base_params["ProbeLength"]=100
# base_params["ProbeDistance"]=30
# base_params["GNDRoutingWidth"]=250
#
# base_params["IDTPitch"]=7
# base_params["IDTN_fingers"]=4
# base_params["IDTOffset"]=1
# base_params["IDTLength"]=105
# base_params["IDTCoverage"]=0.5
# base_params["BusLength"]=0.5
# base_params["EtchWidth"]=0.4
# base_params["AnchorLength"]=4
# base_params["AnchorWidth"]=0.5
# base_params["AnchorEtchMarginX"]=0.45
# base_params["AnchorEtchMarginY"]=0.2
#54
# base_params["ExtConnLength"]=0.5*7
#
# base_params["ViaSize"]=40
# base_params["ViaAreaX"]=300
# base_params["ViaAreaY"]=300
# base_params["ViaShape"]='rectangle'
# base_params["Overvia"]=2
#
# d.import_params(base_params)
#
# d._stretch_top_margin=True
#
# d.view()

# check_cell(verniers())
# check_cell(alignment_marks_4layers())
# check_cell(resistivity_test_cell())
check_cell(chip_frame())
# print(d.resistance())
# p=PArraySeries(d)
# v=check_cell(verniers([0.25,0.5,1 ]))
# p.x_param=[\
# SweepParam({'IDTN_fingers':[5,10,15,20]}),\
# SweepParam({'IDTLength':[20,40,60]})]
# SweepParam({'ViaSize':[10,20,50]})]

# p.view()
# rpq=1

# print(d.resistance(res_per_square=rpq))

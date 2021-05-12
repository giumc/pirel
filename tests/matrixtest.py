from PyResLayout import *
import numpy as np

dut=array(Scaled(LFERes),3)
probe=addLargeGnd(GSGProbe)
device=addProbe(dut,probe)(name="HI")

param=device.export_params()

param["IDTPitch"]=7

param["IDTN"]=4

param["IDTYOffset"]=1

param["IDTLength"]=150/7

param["IDTCoverage"]=0.5

param["BusSizeY"]=0.5

param["EtchX"]=0.4

param["AnchorSizeY"]=4

param["AnchorSizeX"]=0.1

param["AnchorEtchMarginX"]=0.2

param["AnchorEtchMarginY"]=0.2

param["BusExtLength"]=5

param["ProbePitch"]=200

param["ProbeSize"]=100

param["GndRoutingWidth"]=150

device.import_params(param)

param1=SweepParam({"IDTCoverage":[0.3,0.5,0.7]})

param2=SweepParam({"BusSizeY":[2,4,8]})

array=PArray(device,param1.combine(param2),name="HiArray")

array.x_spacing=200

array.auto_labels()

array.view()

mat=PMatrix(device,\
param1.combine(param2),\
SweepParam({"AnchorSizeX":[0.1, 0.3,0.6]}),name="Hi")

mat.x_spacing=200

mat.y_spacing=400

mat.auto_labels(col_index=3,row_index=3)

mat.view()

print(mat.table)
# fig=mat.plot_param('Resistance')
# import cProfile
# import pstats
# profile = cProfile.Profile()
# profile.runcall(export_matrix_data,mat,path=os.path.dirname(__file__),param='Resistance')
# ps = pstats.Stats(profile)
# ps.sort_stats('cumtime')
# ps.print_stats(20)

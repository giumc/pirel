from PyResLayout import *
import numpy as np

# dut=array(calibration(Scaled(LFERes),'open'),3)
# dut=addVia(array(Scaled(FBERes),3),'top')(name='Hey')
probe=addLargeGnd(GSGProbe)
# device=addProbe(dut,probe)(name="HI")

device=probe(name='HI')

param=device.export_params()

param["IDTPitch"]=7

param["IDTN"]=4

param["IDTYOffset"]=1

param["IDTLength"]=150

param["IDTCoverage"]=0.5

param["BusSizeY"]=0.5

param["EtchX"]=0.4

param["AnchorSizeY"]=4

param["AnchorSizeX"]=0.1

param["AnchorEtchMarginX"]=0.2

param["AnchorEtchMarginY"]=0.2

param["PlatePosition"]='in, long'

param["ViaAreaX"]=100
param["ViaAreaY"]=100
param["ViaSize"]=20
param["ViaDistance"]=10

param["ProbePitch"]=100

param["ProbeSizeX"]=10

param["ProbeSizeY"]=10

param["GndRoutingWidth"]=150

# param["SizeX"]=10
#
# param["SizeY"]=10

# device.probe._pad_position='top'

device._pad_position='top'
device.import_params(param)

print(device)
# device.probe._pad_position='top'

# param1=SweepParam({"IDTCoverage":[0.3,0.5,0.7]})

param2=SweepParam({"Pitch":[50,100,150]})

# array=PArray(device,param1.combine(param2),name="HiArray")
array=PArray(device,param2,name="HiArray")

array.x_spacing=200

array.auto_labels()

array.view()

# exit()

mat=PMatrix(device,\
param2,\
param2,name="Hi")

mat.device.fixture_type='short'

mat.x_spacing=200

mat.y_spacing=400

mat.auto_labels(col_index=3,row_index=3)

mat.view()

# print(mat.table)
# fig=mat.plot_param('Resistance')
# import cProfile
# import pstats
# profile = cProfile.Profile()
# profile.runcall(mat.draw)#,path=os.path.dirname(__file__),param='Resistance')
# ps = pstats.Stats(profile)
# ps.sort_stats('tottime')
# ps.print_stats(20)

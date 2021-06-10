# import pirel.modifiers as pm
# import pirel.pcells as pc
# import pirel.tools as pt
# import pirel.sweeps as ps
# import numpy as np
#
# # dut=array(calibration(Scaled(LFERes),'open'),3)
# dut=pm.addVia(pm.array(pm.Scaled(pm.addPartialEtch(pc.FBERes)),3),'top')
# probe=pm.addLargeGnd(pc.GSGProbe)
# device=pm.addProbe(dut,probe)(name="HI")
# # device=dut(name='Hi')
# # device=probe(name='HI')
#
# # pt.check(device.draw())
#
# param=device.export_params()
#
# param["IDTPitch"]=7
#
# param["NBlocks"]=4
#
# param["IDTN"]=8
#
# param["IDTYOffset"]=1
#
# param["IDTLength"]=150
#
# param["IDTCoverage"]=0.5
#
# param["BusSizeY"]=0.5
#
# param["EtchX"]=0.4
#
# param["AnchorSizeY"]=4
#
# param["AnchorSizeX"]=0.1
#
# param["AnchorEtchMarginX"]=0.2
#
# param["AnchorEtchMarginY"]=0.2
#
# param["PlatePosition"]='in, long'
#
# param["ViaAreaX"]=100
# param["ViaAreaY"]=100
# param["ViaSize"]=20
# param["ViaDistance"]=10
#
# param["ProbePitch"]=100
#
# param["ProbeSizeX"]=10
#
# param["ProbeSizeY"]=10
#
# param["GndRoutingWidth"]=150
#
# param["SizeX"]=10
#
# param["SizeY"]=10
#
# param['PadPosition']='top'
#
# device.import_params(param)
#
# print(device)
# # device.probe._pad_position='top'
#
# param1=ps.SweepParam({"IDTCoverage":[0.3,0.5,0.7]})
#
# param2=ps.SweepParam({"ProbePitch":[50,100,150]})
# array=ps.PArray(device,param1,name="HiArray")
# # array=PArray(device,param1.combine(param2),name="HiArray")
# # array=ps.PArray(device,param2,name="HiArray")
#
# array.x_spacing=200
#
# array.auto_labels()
#
# pt.check(array.draw())
#
# mat=ps.PMatrix(device,\
# param1,\
# param2,name="Hi")
#
# mat.x_spacing=200
#
# mat.y_spacing=400
#
# mat.auto_labels(col_index=3,row_index=3)
#
# mat.view()

import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt

dut=pm.addPad(pm.array(pc.LFERes))(name='SweptDevice')

pt.check(dut.draw(),joined=True)

import pirel.sweeps as ps

x_param=ps.SweepParam({'IDTCoverage':[0.3,0.5,0.7],'IDTPitch':[4,8,12]})

y_param1=ps.SweepParam({'NBlocks':[3,4]})
# y_param2=ps.SweepParam({'AnchorSizeX':[5,40]})

# y_param=y_param1.combine(y_param1)

dut_matrix=ps.PMatrix(dut,x_param,y_param1)

dut_matrix.view(blocking=True)

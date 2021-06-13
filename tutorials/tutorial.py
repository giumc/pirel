import pirel.modifiers as pm
import pirel.pcells as pc
import pirel.tools as pt
# d=IDT()
# params=d.export_params()
#
# params["ActiveAreaMargin"]=2.0
# params["N"]=4
#
# d.import_params(params)
# print(d)
# d.view()
# exit()

# p=pm.addLargeGnd(pc.GSGProbe)(name='Hi')
# p.pad_position='top'
# pt.check(p.draw())
# exit()


# q=Bus()
# print(q)
# q.view()
# exit()
#
# d=EtchPit()
# print(d)
# d.view()
# exit()
#
# d=Anchor()
# # print(d)
# t=d.export_params()
# t["EtchMarginY"]=15
# t["EtchMarginX"]=1
# t["SizeX"]=40
# t["SizeY"]=40

# d.import_params(t)
#
# print(d)
# d.view()
# exit()

# d=Via()
# print(d)
# d.view()
# exit()

# exit()
#
# import phidl
# import phidl.geometry as pg
# from PyResLayout import LayoutDefault as ld
#
# d=generate_gds_from_image( r"C:\Users\giuse\Desktop\NewCode\WARP_Layout\NEU logo.png",\
#     layer=ld.layerTop,threshold=0.3,pixelsize=1,size=2048,invert=True)
#
# d=phidl.geometry.import_gds(str(d.absolute()))
# check_cell(d)
#
# d=generate_gds_from_image( r"C:\Users\giuse\Desktop\NewCode\WARP_Layout\DARPAlogo.png",\
#     layer=ld.layerTop,threshold=0.3,pixelsize=1,size=4096)
# d=phidl.geometry.import_gds(str(d.absolute()))
# check_cell(d)
# d=LFERes()
# t=d.export_params()
# t["IDTLength"]=200
# t["IDTNFingers"]=10
# t["AnchorEtchMarginY"]=5
# t["AnchorEtchMarginX"]=5
# t["AnchorSizeX"]=40
# t["AnchorSizeY"]=40
# t["EtchX"]=160
# t["PlatePosition"]='out, long'
# d.import_params(t)
# print(d)
# d.view()
# exit()
# exit()
# d=TFERes()
# print(d)
# d.view()
# exit()

# FBERes().view()

# TFERes().view()

# d=addPad(TFERes)()
# # print(d)
# param=d.export_params()
# param['PadSize']=150
# param['PadDistance']=100
# d.import_params(param)
# d.view()
# exit()

d=pm.Scaled(pc.TFERes)()
param=d.export_params()
param["IDTPitch"]=7
param["IDTN"]=4
param["IDTYOffset"]=1
param["IDTLength"]=10
param["IDTCoverage"]=0.5
param["BusSizeY"]=0.5
param["EtchX"]=0.4
param["AnchorSizeY"]=4
param["AnchorSizeX"]=0.5
param["AnchorEtchMarginX"]=0.2
param["AnchorEtchMarginY"]=0.2
d.import_params(param)

pt.check(d.draw())

exit()
#
# d=array(Scaled(LFERes),3)()
# param=d.export_params()
# param["IDTPitch"]=7
# param["IDTN"]=4
# param["IDTYOffset"]=1
# param["IDTLength"]=10
# param["IDTCoverage"]=0.5
# param["BusSizeY"]=0.5
# param["EtchX"]=0.4
# param["AnchorSizeY"]=4
# param["AnchorSizeX"]=0.5
# param["AnchorEtchMarginX"]=0.2
# param["AnchorEtchMarginY"]=0.2
# d.import_params(param)
# print(d)
# d.view()
# exit()
#
# d=addVia(LFERes)()
#
# p=d.export_params()
# p["ViaType"]='square'
# p['ViaAreaX']=300
# p['ViaAreaY']=300
# p['ViaSize']=30
# p['ViaDistance']=30
# p['OverVia']=3
#
# d.import_params(p)
#
# print(d)
# d.view()
# exit()
# #
# device=addVia(Scaled(array(LFERes,3)))
# probe=addLargeGnd(GSGProbe)
# d=addProbe(device,probe)("tutorial")
#
# param=d.export_params()
# print(d)
# param["IDTPitch"]=7
# param["IDTN"]=8
# param["IDTYOffset"]=1
# param["IDTLength"]=200/7
# param["IDTCoverage"]=0.5
# param["BusSizeY"]=4
# param["EtchX"]=0.4
# param["AnchorSizeY"]=3
# param["AnchorSizeX"]=0.2
# param["AnchorEtchMarginX"]=0.2
# param["AnchorEtchMarginY"]=0.2
# # param['ViaAreaX']=300
# # param['ViaAreaY']=300
# # param['ViaSize']=30
# # param['OverVia']=1.5
# # param['ViaDistance']=100
#
# d.import_params(param)
#
# print(d)
# d.view()
# exit()
# #
probe=addLargeGnd(GSGProbe)

device=array(calibration(Scaled(FBERes),'short'),3)

dut=addProbe(device,probe)

# dut=addProbe(array(calibration(Scaled(FBERes),'short'),3),GSGProbe)#bondstack(Scaled(FBERes),3)

d=dut(name="tutorial")
# print(d)

param=d.export_params()
param["IDTPitch"]=7
param["PlatePosition"]='in, short'
param["IDTN"]=2
param["IDTYOffset"]=1
param["IDTLength"]=10
param["IDTCoverage"]=0.5
param["BusSizeY"]=0.5
param["EtchX"]=0.4
param["AnchorSizeY"]=0.5
param["AnchorSizeX"]=0.5
param["AnchorEtchMarginX"]=0.2
param["AnchorEtchMarginY"]=0.2
param["PadSize"]=10
param["PadDistance"]=5
# param['ViaAreaX']=300
# param['ViaAreaY']=300
# param['ViaSize']=30
# param['OverVia']=1.5
# param['ViaDistance']=100
# param['ProbeGroundSize']=250

d.import_params(param)

d.view()

print(d)

exit()

p=device("tut")

param=p.export_params()
param["IDTPitch"]=7
param["IDTN"]=8
param["IDTYOffset"]=1
param["IDTLength"]=10
param["IDTCoverage"]=0.5
param["BusSizeY"]=0.5
param["EtchX"]=0.4
param["AnchorSizeY"]=0.5
param["AnchorSizeX"]=0.5
param["AnchorEtchMarginX"]=0.2
param["AnchorEtchMarginY"]=0.2
param['ViaAreaX']=300
param['ViaAreaY']=300
param['ViaSize']=30
param['OverVia']=1.5
param['ViaDistance']=100
param['ProbeGroundSize']=250

p.import_params(param)

p.view()

print(p)
# d=alignment_marks_4layers()
#
# check_cell(d)
# exit()
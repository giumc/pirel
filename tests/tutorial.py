from PyResLayout import *

# d=IDT()
# print(d)
# d.view()
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
# print(d)
# t=d.export_params()
# t["EtchMarginY"]=55
# t["EtchMarginX"]=5
# t["SizeX"]=40
# t["SizeY"]=40
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
# # d=FBERes()
# t=d.export_params()
# t["IDTLength"]=200
# t["IDTNFingers"]=10
# t["AnchorEtchMarginY"]=5
# t["AnchorEtchMarginX"]=5
# t["AnchorSizeX"]=40
# t["AnchorSizeY"]=40
# t["EtchX"]=160
# t["PlatePosition"]='in, long'
# d.import_params(t)
# print(d)
# d.view()
#
# exit()
# d=TFERes()
# print(d)
# d.view()
# exit()

# FBERes().view()

# TFERes().view()

# d=addPad(TFERes)()
# print(d)
# param=d.export_params()
# param['PadSize']=150
# param['PadDistance']=100
# d.import_params(param)
# d.view()
# exit()

# d=Scaled(TFERes)()
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
#
# print(d)
# d.view()
#exit()
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
#
# d=addProbe(Scaled(array(LFERes,3)),addLargeGnd(GSGProbe))()
#
# param=d.export_params()
#
# param["IDTPitch"]=7
# param["IDTN"]=8
# param["IDTYOffset"]=1
# param["IDTLength"]=100
# param["IDTCoverage"]=0.5
# param["BusSizeY"]=4
# param["EtchX"]=100
# param["AnchorSizeY"]=3
# param["AnchorSizeX"]=0.2
# param["AnchorEtchMarginX"]=0.2
# param["AnchorEtchMarginY"]=0.2
# param['ViaAreaX']=300
# param['ViaAreaY']=300
# param['ViaSize']=30
# param['OverVia']=1.5
# param['ViaDistance']=100
#
# d.import_params(param)
#
# print(d)
# d.view()
# # exit()
d=calibration(addProbe(addVia(array(Scaled(LFERes),3)),addLargeGnd(GSGProbe)),'short')("tutorial")
# print(d)

param=d.export_params()
param["IDTPitch"]=7
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
param['ViaAreaX']=300
param['ViaAreaY']=300
param['ViaSize']=30
param['OverVia']=1.5
param['ViaDistance']=100
param['ProbeGroundSize']=250

d.import_params(param)

d.view()

exit()

# d=alignment_marks_4layers()
# #
# check_cell(d)
# exit()

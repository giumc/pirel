from sketch import *

# d=IDT()
# print(d)
# d.view()
# exit()

# d=Bus()
# print(d)
# d.view()
# exit()

# d=EtchPit()
# print(d)
# d.view()
# exit()

# d=Anchor()
# print(d)
# d.view()
# exit()

# d=Via()
# print(d)
# d.view()
# exit()

# d=LFERes()
# print(d)
# d.view()
# exit()

# d=FBERes()
# print(d)
# d.view()
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
# print(d)
# param=d.export_params()
# param["IDTPitch"]=7
# param["IDTN_fingers"]=4
# param["IDTOffset"]=1
# param["IDTLength"]=10
# param["IDTCoverage"]=0.5
# param["BusLength"]=0.5
# param["EtchWidth"]=0.4
# param["AnchorLength"]=4
# param["AnchorWidth"]=0.5
# param["AnchorEtchMarginX"]=0.2
# param["AnchorEtchMarginY"]=0.2
# d.import_params(param)
# d.view()
# exit()

# d=array(LFERes,3)()
# d.idt.n=6
# print(d)
# d.view()
# exit()

# d=addVia(LFERes)()
# print(d)
# p=d.export_params()
# p['ViaAreaX']=300
# p['ViaAreaY']=300
# d.import_params(p)
# d.view()
# exit()

# d=addProbe(array(LFERes,3),addLargeGnd(GSGProbe))()
# d.idt.n=6
# print(d)
# d.view()
# exit()
# d=addProbe(addVia(array(Scaled(LFERes),3)),GSGProbe)()
# print(d)
#
# param=d.export_params()
# param["IDTPitch"]=7
# param["IDTN_fingers"]=4
# param["IDTOffset"]=1
# param["IDTLength"]=10
# param["IDTCoverage"]=0.5
# param["BusLength"]=0.5
# param["EtchWidth"]=0.4
# param["AnchorLength"]=4
# param["AnchorWidth"]=0.5
# param["AnchorEtchMarginX"]=0.2
# param["AnchorEtchMarginY"]=0.2
# param['ViaAreaX']=100
# param['ViaAreaY']=100
# param['ViaSize']=10
# param['ViaDistance']=50
# d.import_params(param)
# d.view()
# exit()

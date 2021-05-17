from PyResLayout import *

d=bondstack(addVia(Scaled(LFERes),'top'),3) ()

p=d.export_params()

print(p)
p["IDTLength"]=10
p['ViaAreaX']=100
p['ViaAreaY']=50
p['OverVia']=3
p['ViaSize']=10

d.import_params(p)

print(d)

d.view()

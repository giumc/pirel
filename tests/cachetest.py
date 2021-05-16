from PyResLayout import *

d=Scaled(LFERes) ()

d.view()
d.view()

p=d.export_params()

p["IDTLength"]=10

d.import_params(p)

d.view()

d.view()

p["IDTN"]=4
p["IDTLength"]=20

d.import_params(p)

d.view()

d.view()

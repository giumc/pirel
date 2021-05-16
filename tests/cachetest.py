from PyResLayout import *

d=IDT()

d.view()

p=d.export_params()

p["Length"]=100

d.import_params(p)

print(d)
d.view()
print(d)
d.view()

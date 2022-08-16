import phidl.geometry as pg
import phidl.device_layout as dl
import phidl.path as pp
from phidl import quickplot as qp
from phidl import set_quickplot_options
set_quickplot_options(blocking=True)
p1=(0,0)
p2=(0,30)
p3=(0,30)
p4=(0,60)
p5=(0,60)
# p4=(20,2000)

p=dl.Path((p1,p2,p3,p4,p5))
c=p.extrude(width=10,layer=1)

qp(c)

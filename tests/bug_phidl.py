import phidl.geometry as pg
import phidl.device_layout as dl
import phidl.path as pp
from phidl import quickplot as qp
from phidl import set_quickplot_options
set_quickplot_options(blocking=True)
p1=(0,0)
p2=(0,40)
p3=(20,1600)
p4=(20,2000)

path=pp.smooth(points=(p1,p2,p3,p4),radius=0.1,num_pts=1000)

qp(path)

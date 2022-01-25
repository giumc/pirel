import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps


# d=pm.Scaled(pc.IDT)
# ?
# d.view()

d=pm.connectPorts(pm.makeArray(pc.FBERes),
    tags=('top','bottom'),
    layers=(pt.LayoutDefault.layerTop,pt.LayoutDefault.layerBottom),
    distance=25.0)()

d.view()

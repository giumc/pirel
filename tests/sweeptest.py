import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as pf
import pirel.sweeps as ps

device=pm.addOnePortProbe(
    pm.makeArray(pm.makeScaled(pc.TFERes)),
    probe=pc.GSGProbe)()

# device=pm.makeArray(pc.TFERes)()
arr=ps.PArray(device,ps.SweepParam({"IDTN":[3,5]}))
arr.auto_labels()
pt.check(arr.draw())

import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps5


a=pc.Anchor()
print(a)
a.view()
ma=pc.MultiAnchor()
print(ma)
ma.view()

# idt=pc.IDT()
# idt.view()
#
# idt_pe=pc.PartialEtchIDT()
#
# idt_pe.view()

lferes=pc.LFERes()
print(lferes)
lferes.view()

import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps5


#

# a=pc.Anchor()
# print(a)
# a.view()

# ma=pc.MultiAnchor()

# print(ma)
# ma.view()
#
# idt=pc.IDTSingle()
# idt.view()
#
# idt=pc.IDT()
# idt.view()

# tdmr=pc.TwoDMR()
#
# tdmr.idt.pitch=10
# tdmr.anchor.n=1
#
# print(tdmr)
#
# tdmr.view()
#
# idt_pe=pc.PartialEtchIDT()
#
# idt_pe.view()

# lferes=pc.LFERes()
# print(lferes)
# lferes.view()

# lferes=pc.FBERes()
# print(lferes)
# lferes.plate_under_bus=False
# lferes.plate_over_etch=False
# lferes.view()

lferes=pc.TwoPortRes()

print(lferes)

lferes.view()

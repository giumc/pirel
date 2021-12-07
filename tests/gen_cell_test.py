import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps
# # t=pc.TwoPortRes('hey')
t_aux=pm.makeSMDCoupledFilter(pc.TwoPortRes,
smd=pm.addPassivation(pc.SMD))('hey')
# t['Layer']=pt.LayoutDefault.layerBottom
t_aux.spacing=pt.Point(0,250)
# print(t)

# t.view()

# t_aux=pm.addTwoPortProbe(
#     pm.makeSMDCoupledFilter(
#         pc.TwoPortRes,
#         smd=pm.addPassivation(pc.SMD)),
#     probe=pm.makeTwoPortProbe(pc.GSGProbe))('bu')

t_aux['ProbePadSize']=pt.Point(100,100)
t_aux['RoutingLayer']=(1,)
t_aux['PassivationMargin']=pt.Point(8,4)
# t.spacing=pt.Point(0,250)
t_aux.view()
# main_cell=pc.IDT("hey").draw()
# main_cell.write_gds('hey')

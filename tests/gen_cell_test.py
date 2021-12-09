import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps
# # t=pc.TwoPortRes('hey')
t_aux=pm.addTwoPortProbe(
    pm.makeSMDCoupledFilter(pc.TwoPortRes,
    smd=pm.addPassivation(pc.SMD)),
    probe=pm.makeTwoPortProbe(pm.addLargeGround(pc.GSGProbe)))('hey')

# t_aux=pm.makeSMDCoupledFilter(pc.TwoPortRes,
#     smd=pm.addPassivation(pc.SMD))('hey')
# t_aux=pm.addPassivation(pc.SMD)('hey')
# t['Layer']=pt.LayoutDefault.layerBottom
# t_aux.spacing=pt.Point(0,250)
t_aux.smd.passivation_layer=(1,3)
t_aux.smd.set_01005()
t_aux.smd.passivation_scale=pt.Point(3,2)
t_aux.smd.passivation_margin=pt.Point(10,10)
t_aux.probe.gnd_size=650
# print(t)

# t.view()

# t_aux=pm.addTwoPortProbe(
#     pm.makeSMDCoupledFilter(
#         pc.TwoPortRes,
#         smd=pm.addPassivation(pc.SMD)),
#     probe=pm.makeTwoPortProbe(pc.GSGProbe))('bu')

# t_aux['ProbePadSize']=pt.Point(100,100)
# t_aux['RoutingLayer']=(1,)

t_aux.view()
# main_cell=pc.IDT("hey").draw()
# main_cell.write_gds('hey')

import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps
# # t=pc.TwoPortRes('hey')
t_aux=pm.addTwoPortProbe(
    pm.makeSMDCoupledFilter(pm.makeScaled(pc.TwoPortRes),
    smd=pm.addPassivation(pc.SMD)),
    probe=pm.makeTwoPortProbe(pm.addLargeGround(pc.GSGProbe)))('hey')

# t_aux=pm.makeSMDCoupledFilter(pc.TwoPortRes,
#     smd=pm.addPassivation(pc.SMD))('hey')
# t_aux=pm.addPassivation(pc.SMD)('hey')
# t['Layer']=pt.LayoutDefault.layerBottom
# t_aux.spacing=pt.Point(0,250)
t_aux.smd.passivation_layer=(3,)
t_aux.smd.set_01005()
t_aux.smd.passivation_scale=pt.Point(2.5,1.5)
t_aux.smd.passivation_margin=pt.Point(50,50)
t_aux.probe.ground_size=200
t_aux['IDTLength']=250
t_aux['AnchorSizeX']=0.2
t_aux['AnchorSizeY']=5
t_aux['IDTPitch']=7
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
# t_aux.draw().write_gds("TestSMDFilter")
# main_cell=pc.IDT("hey").draw()
# main_cell.write_gds('hey')

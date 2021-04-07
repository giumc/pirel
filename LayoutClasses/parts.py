
from phidl.device_layout import Device, Port, DeviceReference

import phidl.geometry as pg

from phidl import quickplot as qp

import gdspy

import numpy as np

from abc import ABC, abstractmethod

from tools import LayoutDefault,LayoutTool,Point

class LayoutPart(ABC) :

    def __init__(self,name='default'):

        ld=LayoutDefault()

        self.name=name

        self.origin=ld.origin

    @abstractmethod
    def draw(self):
        pass

    def test(self):

        lib=gdspy.GdsLibrary('hi')
        lib.add(self.draw())
        gdspy.LayoutViewer(lib)
        input()
        exit()

class IDT(LayoutPart) :

    def __init__(self,*args,**kwargs):

        ld=LayoutDefault()

        super().__init__(*args,**kwargs)

        self.y = ld.IDT_y

        self.pitch = ld.IDTpitch

        self.y_offset = ld.IDTy_offset

        self.coverage = ld.IDTcoverage

        self.layer = ld.IDTlayer

        self.n = ld.IDTn

    def draw(self):

        o=self.origin

        rect=pg.rectangle(size=(self.coverage*self.pitch,self.y),\
            layer=self.layer)

        rect.move(origin=(0,0),destination=o.get_coord())

        rect2=pg.copy(rect).move(origin=o.get_coord(),\
                destination=(o+Point(self.pitch,self.y_offset)).get_coord())

        rect.add(rect2)

        cell_tot=pg.connector(midpoint=(self.pitch/2*self.n,self.y+self.y_offset/2),\
            width=self.pitch*(self.n+self.coverage))

        # cell.name=self.name

        cell_tot.add_array(rect,columns=self.n,rows=1,\
            spacing=(self.pitch*2,0))

        cell_tot.flatten()

        cell_tot.name=self.name

        return cell_tot

    def get_finger_size(self):

        dy=self.y

        dx=self.pitch*self.coverage

        return Point(dx,dy)
#
# class Bus(LayoutPart) :
#
#     def __init__(self,*args,**kwargs):
#
#         ld=LayoutDefault()
#
#         super().__init__(*args,**kwargs)
#
#         self.size=ld.Bussize
#         self.distance=ld.distance
#         self.origin = ld.origin
#         self.layer = ld.layerTop
#
#     def draw(self):
#
#         o=self.origin
#
#         r1=gdspy.Rectangle(o.get_coord(),\
#                 (o+self.size).get_coord(),\
#                 layer=self.layer)
#
#         r2 = gdspy.copy(r1,self.distance.x,self.distance.y);
#
#         cell=gdspy.Cell(self.name)
#
#         cell.add([r1,r2])
#
#         return cell
#
#     def get_anchor_lines(self):
#
#         o=self.origin
#
#         l1=Line(o,o+Point(self.size.x,0))
#         l2=Line(o+self.distance+Point(0,self.size.y),o+self.distance+self.size)
#
#         return [l1,l2]
#
# class EtchPit(LayoutPart) :
#
#     def __init__(self,*args,**kwargs):
#
#         ld=LayoutDefault()
#
#         super().__init__(*args,**kwargs)
#
#         self.active_area=ld.EtchPitactive_area
#
#         self.origin=ld.origin
#
#         self.x=ld.EtchPit_x
#
#         self.anchor_etch=ld.EtchPitanchor_etch
#
#         self.anchor_size=ld.EtchPitanchor_size
#
#         self.layer=ld.layerEtch
#
#         self.etch_margin=ld.EtchPitetch_margin
#
#     def draw(self):
#
#         b_main=Bus(self.name+"Main Etch Pit");
#
#         b_main.origin=self.origin
#
#         b_main.layer=self.layer
#
#         b_main.size=Point(self.x,self.active_area.y+2*self.etch_margin.y)
#
#         b_main.distance=Point(self.active_area.x+self.x+2*self.etch_margin.x,0)
#
#         main_etch=b_main.draw()
#
#         if self.anchor_etch:
#
#             anchor_etch_size=self.get_anchor_etch_size()
#
#             o=b_main.origin-Point(0,anchor_etch_size.y)
#
#             b_anchor_down=Bus(self.name+"anchor_down")
#
#             b_anchor_down.layer=self.layer
#
#             b_anchor_down.origin=o
#
#             b_anchor_down.size=anchor_etch_size
#
#             b_anchor_down.distance=Point(\
#                 2*self.x+2*self.etch_margin.x+self.active_area.x-anchor_etch_size.x,0)
#
#             anchor_etch_down=b_anchor_down.draw()
#
#             anchor_etch_up=anchor_etch_down.copy(b_anchor_down.name+"up",\
#                 translation=Point(0,anchor_etch_size.y+b_main.size.y).get_coord())
#
#             etch=main_etch.add(anchor_etch_up)
#
#             etch=main_etch.add(anchor_etch_down)
#
#             etch.flatten()
#
#         else:
#
#             etch=main_etch.flatten()
#
#         etch.name=self.name
#
#         return etch
#
#     def get_anchor_lines(self):
#
#         o=self.origin
#         p1=o+Point(self.x+self.etch_margin.x,self.etch_margin.y)
#         p2=p1+Point(self.active_area.x,0)
#
#         p3=p1+Point(0,self.active_area.y)
#         p4=p3+Point(self.active_area.x,0)
#
#         if self.anchor_etch:
#
#             dx=-self.x+(self.get_anchor_etch_size()).x
#             dy= 0
#
#             p1=p1+Point(dx,dy)
#             p2=p2+Point(-dx,dy)
#             p3=p1+Point(dx,-dy)
#             p4=p2+Point(-dx,-dy)
#
#         return [Line(p1,p2), Line(p3,p4)]
#
#     def get_anchor_etch_size(self):
#
#         return Point((self.active_area.x+2*self.x-self.anchor_size.x)/2,\
#             self.anchor_size.y)
#
# class BaseLFEResonator(LayoutPart):
#
#     def __init__(self,*args,**kwargs):
#
#         super().__init__(*args,**kwargs)
#
#         self.idt=IDT(name='ResIDT')
#
#         self.bus=Bus(name='ResBus')
#
#         self.etchpit=EtchPit(name='ResEtchPit')
#
#         self.anchor=Bus(name='ResAnchor')
#
#         self.anchor.size=self.etchpit.anchor_size
#
#     def draw(self):
#
#         idt_cell=self.idt.draw()
#
#         self.bus.origin=self.idt.origin-Point(0,self.bus.size.y)
#
#         self.bus.size=Point(2*self.idt.pitch*(self.idt.n-1)+(1+self.idt.coverage)*self.idt.pitch,\
#             self.bus.size.y)
#
#         self.bus.distance=Point(0,self.bus.size.y+self.idt.y+self.idt.y_offset)
#
#         bus_cell = self.bus.draw()
#
#         self.etchpit.etch_margin.x=self.idt.pitch*(1-self.idt.coverage)/2
#
#         self.etchpit.origin=self.bus.origin-Point(self.etchpit.x+self.etchpit.etch_margin.x,\
#             self.etchpit.etch_margin.y)
#
#         self.etchpit.active_area=LayoutTool().get_size(bus_cell)
#
#         self.etchpit.anchor_size=self.anchor.size-Point(0,self.etchpit.etch_margin.y)
#
#         etchpit_cell = self.etchpit.draw()
#
#         self.anchor.origin = (self.etchpit.get_anchor_lines()[0]).p1-\
#         Point(0,self.anchor.size.y)
#
#         self.anchor.distance=Point(0,self.anchor.size.y+self.etchpit.active_area.y)
#
#         anchor_cell=self.anchor.draw()
#
#         cell=LayoutTool().merge_cells(idt_cell,bus_cell,etchpit_cell,anchor_cell,name=self.name)
#
#         return cell
#         # cell.flatten()
#
#     def set_origin(self,p=Point(0,0)):
#
#         self.origin=p;
#         self.idt.origin=p;
#
#     def get_anchor_lines(self):
#
#         pit_lines=self.etchpit.get_anchor_lines()
#
#         anchor_lines=[pit_lines[0].move(Point(0,-self.anchor.size.y)),\
#                     pit_lines[1].move(Point(0,self.anchor.size.y))]
#
#         return anchor_lines
#
# class GSProbe(LayoutPart):
#
#     def __init__(self,*args,**kwargs):
#
#         ld=LayoutDefault()
#
#         super().__init__(*args,**kwargs)
#
#         self.pitch = ld.GSProbepitch
#
#         self.pad_size = ld.GSProbepad_size
#
#         self.routing = ld.GSProberouting
#
#         self.routing_width = ld.GSProberouting_width
#
#         self.layer = ld.GSProbelayer
#
#         self.dut = ld.GSProbedut
#
#         self.spacing = ld.GSProbespacing
#
#     def draw_pads(self):
#
#         bus_aux=Bus(name=self.name+"bus_aux")
#
#         bus_aux.origin=self.origin
#
#         bus_aux.size=self.pad_size
#
#         bus_aux.layer=self.layer
#
#         bus_aux.distance=Point(self.pitch,0)
#
#         return bus_aux.draw()
#
#     def draw(self):
#
#         if self.routing:
#
#             dut_anchor_lines= self.dut.get_anchor_lines()
#
#             bottom_mid_point=dut_anchor_lines[0].get_mid_point()
#
#             self.origin =bottom_mid_point-\
#                 Point(self.pad_size.x/2+self.pitch,self.pad_size.y+self.spacing.y)
#
#             cell_pads=self.draw_pads()
#
#             cell_pads.add(gdspy.Rectangle(\
#             (bottom_mid_point-Point(self.routing_width/2,self.spacing.y)).get_coord(),\
#             (bottom_mid_point+Point(self.routing_width/2,0)).get_coord(),\
#             layer=self.layer))
#
#             if self.dut.get_area().x/2>self.pitch:
#
#             return cell_pads
#
#         else:
#
#             return self.draw_pads()
#
#     def get_anchor_lines(self):
#
#         return self.dut.get_anchor_lines()

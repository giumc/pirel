import gdspy
import numpy as np
from abc import ABC, abstractmethod

from tools import LayoutDefault,LayoutTool

class LayoutPart(ABC) :

    def __init__(self,name='default'):

        ld=LayoutDefault()

        self.name=name

        self.origin=ld.origin

    @abstractmethod
    def draw(self):
        pass

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

        r1=gdspy.Rectangle(o.tolist(),\
            (o+self.get_finger_size()).tolist(),\
            layer=self.layer)

        o_dx=o+np.array([self.pitch,self.y_offset])

        r2=gdspy.Rectangle(o_dx.tolist(),\
            (o_dx+self.get_finger_size()).tolist(),\
            layer=self.layer)

        unitcell=gdspy.Cell('dummy')

        unitcell.add(r1)
        unitcell.add(r2)

        cellout=gdspy.Cell(self.name)

        cellout.add(\
            gdspy.CellArray(unitcell,\
                self.n,1,\
                    np.array([2*self.pitch,0])))

        cellout.flatten()

        cellout.name=self.name

        return cellout

    def get_finger_size(self):

        dy=self.y

        dx=self.pitch*self.coverage

        return np.array([dx,dy])

class Bus(LayoutPart) :

    def __init__(self,*args,**kwargs):

        ld=LayoutDefault()

        super().__init__(*args,**kwargs)

        self.x = ld.Bus_x
        self.y =  ld.Bus_y
        self.distance=ld.distance
        self.origin = ld.origin
        self.layer = ld.layerTop

    def draw(self):

        o=self.origin

        r1=gdspy.Rectangle(o.tolist(),\
                (o+self.get_bus_size()).tolist(),\
                layer=self.layer)

        toporigin=(o+self.distance)

        r2 = gdspy.Rectangle(toporigin.tolist(),\
        (toporigin+self.get_bus_size()).tolist(),\
            layer=self.layer)

        cell=gdspy.Cell(self.name)

        cell.add([r1,r2])

        cell.flatten()

        cell.name=self.name

        return cell

    def get_bus_size(self):

        return np.array([self.x,self.y])

class EtchPit(LayoutPart) :

    def __init__(self,*args,**kwargs):

        ld=LayoutDefault()

        super().__init__(*args,**kwargs)

        self.active_area=ld.EtchPitactive_area

        self.x=ld.EtchPit_x

        self.anchor_etch=ld.EtchPitanchor

        self.anchor_x=ld.EtchPitanchor_x

        self.anchor_y=ld.EtchPitanchor_y

        self.origin=ld.origin

        self.layer=ld.layerEtch

    def draw(self):

        b_main=Bus("Main Etch");

        b_main.origin=self.origin;

        b_main.layer=self.layer

        b_main.x=self.x

        b_main.y=self.active_area[1]

        b_main.distance=np.array([self.active_area[0],0])

        main_etch=b_main.draw()

        if self.anchor_etch:

            o=b_main.origin-np.array([0,self.anchor_y])

            b_anchor=Bus("AnchorEtch")

            b_anchor.layer=self.layer

            b_anchor.origin=o;

            b_anchor.x=self.anchor_x

            b_anchor.y=self.anchor_y

            b_anchor.distance=np.array(\
            [self.anchor_x+b_main.x+2*(self.active_area[0]/2-self.anchor_x),0])

            anchor_etch_down=b_anchor.draw()

            anchor_etch_down.flatten()

            anchor_etch_up=anchor_etch_down.copy("tmp",\
                translation=np.array([0,b_anchor.y+self.active_area[1]]))

            anchor_etch_up.flatten()

            etch=main_etch.add(anchor_etch_up)
            etch=main_etch.add(anchor_etch_down)

            etch.flatten()

        else:

            etch=main_etch.flatten()

        etch.name=self.name

        return etch

class BaseLFEResonator(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.idt=IDT(name='ResIDT')

        self.bus=Bus(name='ResBus')

        self.etchpit=EtchPit(name='ResEtchPit')

    def draw(self):

        cell=gdspy.Cell(self.name)

        idt_cell=self.idt.draw()

        self.bus.distance=np.array(\
        [0,(LayoutTool().get_size(idt_cell))[1]+self.bus.y])

        bus_cell = self.bus.draw()

        self.etchpit.active_area=LayoutTool().get_size(bus_cell)

        etchpit_cell = self.etchpit.draw()

        cell.add(idt_cell.copy('idt_transl',translation=np.array(\
            [self.idt.pitch*(1-self.idt.coverage)/2+self.etchpit.x,\
            self.bus.y])))

        cell.add(bus_cell.copy('bus_transl',translation=np.array(\
            [self.etchpit.x,0])))
        #
        # cell.add(etchpit_cell.copy('etchpit_transl',\
        # translation=np.array([-self.etchpit.x,0])))

        # cell.flatten()

        # cell.add(bus_cell)
        # cell.flatten()

        # cell.add(etchpit_cell)

        return cell
        # cell.flatten()

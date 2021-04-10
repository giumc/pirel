from phidl.device_layout import Device, Port, DeviceReference
import phidl.geometry as pg
from phidl import set_quickplot_options
from phidl import quickplot as qp
import gdspy
from abc import ABC, abstractmethod
from tools import *
import matplotlib.pyplot as plt
import warnings

def save_cell(fun):

    def wrapper(fun):

        cell=fun()

        # self.cell=cell

        print(cell.name)

        return cell

    return wrapper

class LayoutPart(ABC) :

    def __init__(self,name='default'):

        ld=LayoutDefault()

        self.name=name

        self.origin=ld.origin

        self.cell=Device()

    def __init_subclass__(self):

        super().__init_subclass__()

        import pdb; pdb.set_trace()

        self.draw=save_cell(self.draw)

    @abstractmethod
    def draw(self):
        pass

    def test(self):
        set_quickplot_options(blocking=True)
        qp(self.draw())
        return

    def test_gds(self):
        lib=gdspy.GdsLibrary('test')
        lib.add(self.draw())
        gdspy.LayoutViewer(lib)

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

        rect.move(origin=(0,0),destination=o())

        unitcell=Device(name=self.name)

        r1=unitcell << rect
        unitcell.absorb(r1)
        r2 = unitcell << rect

        r2.move(origin=o(),\
        destination=(o+Point(self.pitch,self.y_offset))())

        unitcell.absorb(r2)

        cell=Device()

        cell.name=self.name

        cell.add_array(unitcell,columns=self.n,rows=1,\
            spacing=(self.pitch*2,0))

        cell.flatten()

        totx=self.pitch*(self.n*2-1)-self.pitch*(1-self.coverage)

        midx=totx/2

        finger_dist=Point(self.pitch*1,\
        self.y+self.y_offset)

        cell.add_port(Port(name=self.name,\
        midpoint=(o+\
        Point(midx,0))(),\
        width=totx,
        orientation=-90))

        return cell

    def get_finger_size(self):

        dy=self.y

        dx=self.pitch*self.coverage

        return Point(dx,dy)

class Bus(LayoutPart) :

    def __init__(self,*args,**kwargs):

        ld=LayoutDefault()

        super().__init__(*args,**kwargs)

        self.size=ld.Bussize
        self.distance=ld.distance
        self.origin = ld.origin
        self.layer = ld.layerTop

    def draw(self):

        o=self.origin

        pad=pg.rectangle(size=self.size(),\
        layer=self.layer).move(origin=(0,0),\
        destination=o())


        cell=Device(name=self.name)

        r1=cell<<pad
        cell.absorb(r1)
        r2=cell <<pad

        r2.move(origin=o(),\
        destination=(o+self.distance)())

        cell.absorb(r2)

        cell.add_port(name=self.name,\
        midpoint=(o+Point(self.size.x/2,self.size.y))(),\
        width=self.size.x,\
        orientation=90)

        return cell

class EtchPit(LayoutPart) :

    def __init__(self,*args,**kwargs):

        ld=LayoutDefault()

        super().__init__(*args,**kwargs)

        self.active_area=ld.EtchPitactive_area

        self.origin=ld.origin

        self.x=ld.EtchPit_x

        self.layer=ld.EtchPitlayer

    def draw(self):

        o=self.origin

        b_main=Bus()

        b_main.origin=o

        b_main.layer=self.layer

        b_main.size=Point(self.x,self.active_area.y)

        b_main.distance=Point(self.active_area.x+self.x,0)

        main_etch=b_main.draw()

        etch=Device()

        etch.absorb(etch<<main_etch)

        port_up=Port(self.name+'up',\
        midpoint=(o+Point(self.x+self.active_area.x/2,0))(),\
        width=self.active_area.x,\
        orientation=90)

        port_down=Port(self.name+'down',\
        midpoint=(o+Point(self.x+self.active_area.x/2,0))(),\
        width=self.active_area.x,\
        orientation=-90)

        etch.add_port(port_up)
        etch.add_port(port_down)

        return etch

class Anchor(LayoutPart):

    def __init__(self,*args,**kwargs):

        ld=LayoutDefault()

        super().__init__(*args,**kwargs)

        self.size=ld.Anchorsize
        self.etch_margin=ld.Anchoretch_margin
        self.etch_x=ld.Anchoretch_x
        self.x_offset=ld.Anchoretchx_offset
        self.layer=ld.Anchorlayer
        self.etch_layer=ld.Anchoretch_layer

    def draw(self):

        o=self.origin

        anchor=pg.rectangle(\
            size=self.size(),\
            layer=self.layer)

        etch_size_mid=Point(\
        (self.etch_x-2*self.etch_margin.x-self.size.x)/2,\
        self.size.y-self.etch_margin.y)

        offset=Point(self.x_offset,0)

        etch_sx=pg.rectangle(\
            size=(etch_size_mid-offset)(),\
            layer=self.etch_layer)

        etch_dx=pg.rectangle(\
            size=(etch_size_mid+offset)(),\
            layer=self.etch_layer)

        cell=Device(name=self.name)

        cell.absorb((cell<<etch_sx).move(origin=(0,0),\
        destination=o()))

        anchor_transl=o+Point(etch_sx.size[0]+self.etch_margin.x,0)

        cell.absorb((cell<<anchor).move(origin=(0,0),\
        destination=anchor_transl()))

        etchdx_transl=anchor_transl+Point(anchor.size[0]+self.etch_margin.x,0)
        cell.absorb((cell<<etch_dx).move(origin=(0,0),\
        destination=etchdx_transl()))

        cell.add_port(name=self.name,\
        midpoint=(anchor_transl+Point(self.size.x/2,self.size.y))(),\
        width=self.size.x,\
        orientation=90)

        return cell

class LFERes(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        ld=LayoutDefault()

        self.idt=IDT(name='ResIDT')

        self.bus=Bus(name='ResBus')

        self.etchpit=EtchPit(name='ResEtchPit')

        self.anchor=Anchor(name='ResAnchor')

    def draw(self):

        o=self.origin

        self.idt.origin=o

        idt_cell=self.idt.draw()

        cell=Device(name=self.name)

        idt_ref=cell<<idt_cell

        self.bus.size=Point(\
            2*self.idt.pitch*(self.idt.n-1)+(self.idt.coverage)*self.idt.pitch,\
            self.bus.size.y)

        self.bus.distance=Point(\
            self.idt.pitch,self.bus.size.y+self.idt.y+self.idt.y_offset)

        bus_cell = self.bus.draw()

        bus_ref= cell<<bus_cell

        ports=cell.get_ports()

        bus_ref.connect(port=ports[1],\
        destination=ports[0])

        cell.absorb(idt_ref)


        self.etchpit.active_area=Point().from_iter(cell.size)+\
        Point(self.idt.pitch*(1-self.idt.coverage),self.anchor.etch_margin.y*2)

        etch_cell=self.etchpit.draw()

        etch_ref=cell<<etch_cell

        ports=cell.get_ports()
        etch_ref.connect(ports[2],\
        destination=ports[0])

        etch_ref.move(origin=etch_ref.center,\
        destination=(Point().from_iter(etch_ref.center)+\
            Point(self.idt.pitch/2,-self.bus.size.y-self.anchor.etch_margin.y))())

        cell.absorb(bus_ref)

        self.anchor.etch_x=self.etchpit.x*2+self.etchpit.active_area.x

        anchor_cell=self.anchor.draw()

        anchor_bottom=cell<<anchor_cell

        ports=cell.get_ports()

        anchor_bottom.connect(ports[2],
        destination=ports[1],overlap=self.anchor.etch_margin.y)
        anchor_bottom.move(origin=(0,0),\
        destination=(-self.anchor.x_offset,0))

        anchor_top=(cell<<anchor_cell)
        anchor_top.move(origin=anchor_top.center,\
        destination=anchor_bottom.center)
        anchor_pivot=ports[2]

        anchor_top.rotate(angle=180,center=ports[1].center)
        anchor_top.move(origin=(0,0),\
        destination=(0,self.etchpit.active_area.y))

        cell.absorb(etch_ref)

        ports=cell.get_ports()
        ports[0].rotate(180,center=ports[0].center)
        ports[1].rotate(180,center=ports[1].center)

        cell.absorb(anchor_top)
        cell.absorb(anchor_bottom)

        cell_out=join(cell)
        cell_out.add_port(Port(name=self.name+"Top",\
        midpoint=(Point().from_iter(ports[1].center)+\
        Point(0,self.anchor.size.y))(),\
        width=self.anchor.size.x,\
        orientation=-90))

        cell_out.add_port(Port(name=self.name+"Bottom",\
        midpoint=(Point().from_iter(ports[0].center)-\
        Point(0,self.anchor.size.y))(),\
        width=self.anchor.size.x,\
        orientation=90))



        return cell_out

class FBERes(LFERes):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        ld=LayoutDefault()
        self.platelayer=ld.FBEResplatelayer

    def draw(self):

        cell=LFERes.draw(self)

        plate=pg.rectangle(size=self.etchpit.active_area(),\
        layer=self.platelayer)

        plate_ref=cell<<plate

        transl_rel=Point(self.etchpit.x,self.anchor.size.y-self.anchor.etch_margin.y)
        lr_cell=get_corners(cell)[0]
        lr_plate=get_corners(plate_ref)[0]
        plate_ref.move(origin=lr_plate(),\
        destination=(lr_plate+lr_cell+transl_rel)())

        cell.absorb(plate_ref)



        return cell

class Via(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        ld=LayoutDefault()

        self.layer=ld.Vialayer
        self.__type=ld.Viatype
        self.size=ld.Viasize

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self,string):

            if not (string=='circle' or string=='rectangle'):

                raise Exception("Vias can be only 'circle' or 'rectangle' for now")

            else:

                self.__type=string

    def draw(self):

        if self.type=='rectangle':

            if isinstance(self.size,Point):

                cell=pg.rectangle(size=self.size(),\
                    layer=self.layer)

            elif isinstance(self.size,int) or isinstance(self.size,float):

                cell=pg.rectangle(size=(self.size,self.size),\
                    layer=self.layer)

            else:

                raise Exception("Via.size has to be Point or int/float")

        elif self.type=='circle':

            if isinstance(self.size,Point):

                cell=pg.circle(radius=self.size.x,\
                layer=self.layer)

            elif isinstance(self.size,int) or isinstance(self.size,float):

                cell=pg.circle(radius=self.size,\
                layer=self.layer)

            else:

                raise Exception("Via.size has to be Point or int/float")

        else:

            raise Exception("Something went wrong,abort")

        cell.move(origin=(0,0),\
            destination=self.origin())

        cell.name=self.name

        cell.add_port(Port(name=self.name,\
        midpoint=cell.center,\
        width=cell.xmax-cell.xmin,\
        orientation=90))



        return cell

class TFERes(LFERes):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

    def draw(self):

        cell=LFERes.draw(self)

        # idt_ref=cell<<self.idt.cell
        # idt_ref.move(origin=self.idt.origin,\
        # destination=(50,30))

        return self.idt.cell

class GSProbe(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        ld=LayoutDefault()

        self.layer=ld.GSProbelayer
        self.pitch=ld.GSProbepitch
        self.size=ld.GSProbesize

    def draw(self):

        name=self.name

        o=self.origin

        pad_x=self.size.x

        if pad_x>self.pitch*2/3:

            pad_x=self.pitch*2/3

            warnings.warn("Pad size too large, capped to pitch*2/3")

        pad_cell=pg.rectangle(size=(pad_x,self.size.y),\
        layer=self.layer)

        pad_cell.move(origin=(0,0),\
        destination=o())

        cell=Device(name=self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell
        pad_sig.move(origin=o(),\
        destination=(o+dp)())

        cell.add_port(Port(name=self.name,\
        midpoint=(o+Point(pad_x/2+self.pitch,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        return cell

class GSGProbe(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        ld=LayoutDefault()

        self.layer=ld.GSGProbelayer
        self.pitch=ld.GSGProbepitch
        self.size=ld.GSGProbesize

    def draw(self):

        name=self.name

        o=self.origin

        pad_x=self.size.x

        if pad_x>self.pitch*2/3:

            pad_x=self.pitch*2/3

            warnings.warn("Pad size too large, capped to pitch*2/3")

        pad_cell=pg.rectangle(size=(pad_x,self.size.y),\
        layer=self.layer)

        pad_cell.move(origin=(0,0),\
        destination=o())

        cell=Device(name=self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell
        pad_sig.move(origin=o(),\
        destination=(o+dp)())

        pad_gnd_dx=cell<<pad_cell
        pad_gnd_dx.move(origin=o(),\
        destination=(o+dp*2)())

        cell.add_port(Port(name=self.name,\
        midpoint=(o+Point(pad_x/2+self.pitch,self.size.y))(),\
        width=pad_x,\
        orientation=90))



        return cell

class OnePortRouting(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(self,*args,**kwargs)

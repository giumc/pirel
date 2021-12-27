from pirel.tools import *

import pirel.tools as pt

from phidl.device_layout import Device, Port, DeviceReference, Group

import pathlib

import phidl.geometry as pg

import phidl.path as pp

from phidl import set_quickplot_options

from phidl import quickplot as qp

from phidl import Path,CrossSection

import os

import gdspy

import numpy as np

from copy import copy,deepcopy

import matplotlib.pyplot as plt

class Text(LayoutPart):
    ''' Class to store text data and to add it in cells.

    It controls how the text labels generated are formatted.
    You can add text to a cell using the add_text() method.

    Attributes
    -----------
    font : string
            if overridden, needs to be in pirel / path

    size : float

    label :     string
        can be multiline if '\\n' is added

    layer:   int.
    '''

    _valid_names={'font','size','label','layer'}

    _msg_err="""Invalid key for text_param.
    Valid options are :{}""".format("\n".join(_valid_names))

    layer=LayoutParamInterface()

    label=LayoutParamInterface()

    size=LayoutParamInterface()

    font=LayoutParamInterface()

    def __init__(self,*a,**kw):

        super().__init__(*a,**kw)

        self.layer=LayoutDefault.TextLayer

        self.label=LayoutDefault.TextLabel

        self.size=LayoutDefault.TextSize

        self.font=LayoutDefault.TextFont

    def add_to_cell(self,cell,
        angle=0,*a,**kw):
        '''Add text to a cell.

        Parameters
        ---------

        cell : phidl.Device

        angle : float

        optional: options for move_relative_to_cell().
        '''

        text_cell_ref=DeviceReference(self.draw())

        try:

            text_cell_ref.rotate(
                center=pt._anchor_selector(kw['anchor_source'],text_cell_ref).coord,
                angle=angle)

        except:

            text_cell_ref.rotate(
                center=pt._anchor_selector('ll',text_cell_ref).coord,
                angle=angle)

        pt._move_relative_to_cell(text_cell_ref,cell,**kw)

        cell.add(text_cell_ref)

        return cell

    def draw(self):

        cell=Device(self.name)

        for l in self.layer:

            cell<<pg.text(
                size=self.size,
                text=self.label,
                font=self.font,
                layer=l)

        return cell

class IDT(LayoutPart) :
    ''' Generates interdigitated structure.

        Derived from LayoutPart.

        Attributes
        ----------
        y   :float
            finger length

        pitch : float
            finger distance

        y_offset : float
            top/bottom fingers gap

        coverage : float
            finger coverage
        layer : int
            finger layer
        n  : int
            finger number.
    '''

    length =LayoutParamInterface()

    pitch = LayoutParamInterface()

    y_offset =LayoutParamInterface()

    coverage =LayoutParamInterface()

    n =LayoutParamInterface()

    active_area_margin=LayoutParamInterface()

    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.length=LayoutDefault.IDT_y
        self.pitch=LayoutDefault.IDTpitch
        self.y_offset=LayoutDefault.IDTy_offset
        self.coverage=LayoutDefault.IDTcoverage
        self.n=LayoutDefault.IDTn
        self.layer=LayoutDefault.IDTlayer
        self.active_area_margin=LayoutDefault.LFEResactive_area_margin

    def draw(self):
        ''' Generates layout cell based on current parameters.

        'top' and 'bottom' ports are included in the cell.

        Returns
        -------
        cell : phidl.Device.
        '''

        unitcell=self._draw_unit_cell()

        cell=Device(self.name)

        cell.name=self.name

        cell.add_array(unitcell,columns=self.n,rows=1,\
            spacing=(self.pitch*2,0))

        cell.flatten()

        totx=self.pitch*(self.n*2+1)-self.pitch*(1-self.coverage)

        midx=totx/2

        finger_dist=Point(self.pitch*1,\
        self.length+self.y_offset)

        cell=join(cell)

        cell.name=self.name

        cell.add_port(Port(name='bottom',\
        midpoint=(self.origin+\
        Point(midx,0)).coord,\
        width=totx,
        orientation=-90))

        cell.add_port(
            name='top',
            midpoint=Point(midx,self.length+self.y_offset).coord,
            width=totx,
            orientation=90)

        del unitcell

        return cell

    def get_finger_size(self):
        ''' get finger length and width.

        Returns
        -------
        size : PyResLayout.Point
            finger size as coordinates lenght(length) and width(x).
        '''
        dy=self.length

        dx=self.pitch*self.coverage

        return Point(dx,dy)

    @property
    def active_area(self):

        x=self.pitch*(self.n*2+1)+2*self.active_area_margin

        y=self.length+self.y_offset

        return Point(x,y)

    @property
    def probe_distance(self):

        return Point(0,self.active_area.x)

    @property
    def resistance_squares(self):

        return self.length/self.pitch/self.coverage/self.n*2/3

    @classmethod
    def calc_n_fingers(self,c0_dens,z0,f,len):

        from numpy import ceil,floor
        from math import pi

        return int(ceil(1/2/pi/f/c0_dens/z0/len))

    @classmethod
    def calc_length(self,c0_dens,z0,f,n):

        from numpy import ceil

        from math import pi

        if not round(n)==0:

            raise ValueError("{} needs to be integer")

        return 1/2/pi/f/c0_dens/z0/n

    def _draw_unit_cell(self):

        rect=pg.rectangle(size=(self.coverage*self.pitch,self.length),
            layer=self.layer)

        unitcell=Device()

        r1=unitcell << rect

        unitcell.absorb(r1)

        r2 = unitcell << rect

        r2.move(
            destination=Point(self.pitch,self.y_offset).coord)

        r3= unitcell<< rect

        r3.move(
            destination=Point(2*self.pitch,0).coord)

        unitcell.absorb(r2)

        unitcell.absorb(r3)

        unitcell.name="UnitCell"

        del rect

        return unitcell

class PartialEtchIDT(IDT):

    layer_partialetch=pt.LayoutParamInterface()

    def __init__(self,*a,**kw):

        super().__init__(*a,**kw)

        self.layer_partialetch=LayoutDefault.layerPartialEtch

    def _draw_unit_cell(self):

        rect=pg.rectangle(size=(self.coverage*self.pitch,self.length),
            layer=self.layer)

        unitcell=Device()

        r1=unitcell << rect

        unitcell.absorb(r1)

        rect_partialetch=pg.rectangle(
            size=(
                (1-self.coverage)*self.pitch,self.length-self.y_offset),
            layer=self.layer_partialetch)

        rect_partialetch.move(
            destination=(self.pitch*self.coverage,self.y_offset))

        rp1=unitcell<<rect_partialetch

        rp2=unitcell<<rect_partialetch

        rp2.move(destination=(self.pitch,0))

        r2 = unitcell << rect

        r2.move(
            destination=Point(self.pitch,self.y_offset).coord)

        r3= unitcell<< rect

        r3.move(
            destination=Point(2*self.pitch,0).coord)

        rect_partialetch_side=pg.rectangle(
            size=(
                (1-self.coverage)*self.pitch/2,self.length-self.y_offset),
            layer=self.layer_partialetch)

        petch_side1=unitcell<<rect_partialetch_side

        petch_side2=unitcell<<rect_partialetch_side

        petch_side1.move(
            destination=(-petch_side1.xsize,self.y_offset))

        petch_side2.move(
            destination=(self.pitch*2+self.pitch*self.coverage,self.y_offset))

        unitcell.absorb(r2)

        unitcell.absorb(r3)

        unitcell.absorb(petch_side1)

        unitcell.absorb(petch_side2)

        unitcell.name="UnitCell"

        return unitcell

    def draw(self):

        return IDT.draw.__wrapped__(self)

class Bus(LayoutPart) :
    ''' Generates pair of bus structure.

    Derived from LayoutPart.

    Attributes
    ----------
    size : PyResLayout.Point
        bus size coordinates of length(y) and width(x)
    distance : PyResLayout.Point
        distance between buses coordinates
    layer : int
        bus layer.
    '''
    size=LayoutParamInterface()

    distance=LayoutParamInterface()

    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer = LayoutDefault.layerTop

        self.size=copy(LayoutDefault.Bussize)

        self.distance=copy(LayoutDefault.Busdistance)

    def draw(self):
        ''' Generates layout cell based on current parameters.

        'conn' port is included in the cell.

        Returns
        -------
        cell : phidl.Device.
        '''

        pad=pg.rectangle(
            size=self.size.coord,
            layer=self.layer)

        cell=Device(self.name)

        r1=cell<<pad
        cell.absorb(r1)
        r2=cell <<pad

        r2.move(
            destination=self.distance.coord)

        cell.absorb(r2)

        cell.add_port(name='conn',
        midpoint=Point(self.size.x/2,self.size.y).coord,
        width=self.size.x,
        orientation=90)

        return cell

    @property
    def resistance_squares(self):

        return self.size.x/self.size.y/2

class EtchPit(LayoutPart) :
    ''' Generates pair of etching trenches.

    Derived from LayoutPart.

    Attributes
    ----------
    active_area : PyResLayout.Point
        area to be etched as length(Y) and width(X)
    x : float
        etch width
    layer : int
        etch pit layer
    '''

    active_area=LayoutParamInterface()

    x=LayoutParamInterface()

    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.active_area=copy(LayoutDefault.EtchPitactive_area)

        self.x=LayoutDefault.EtchPit_x

        self.layer=LayoutDefault.EtchPitlayer

    def draw(self):
        ''' Generates layout cell based on current parameters.

        'top' and 'bottom' ports is included in the cell.

        Returns
        -------
        cell : phidl.Device.
        '''
        main=pg.rectangle(size=(self.x,self.active_area.y),
            layer=self.layer)

        etch=Device(self.name)

        etch_lx=etch<<main

        etch_rx=etch<<main

        etch_rx.move(destination=(self.x+self.active_area.x,0))

        port_up=Port('top',
        midpoint=Point(self.x+self.active_area.x/2,self.active_area.y).coord,
        width=self.active_area.x,
        orientation=-90)

        port_down=Port('bottom',
        midpoint=Point(self.x+self.active_area.x/2,0).coord,
        width=self.active_area.x,
        orientation=90)

        etch.add_port(port_up)
        etch.add_port(port_down)

        return etch

class Anchor(LayoutPart):
    ''' Generates anchor structure.

    Attributes
    ----------
    size :
        length(Y) and size(X) of anchors

    metalized : PyResLayout.Point
        metal connection

    etch_choice: boolean
        to add or not etching patterns

    etch_x : float
        width of etch pit

    layer : int
        metal layer

    etch_layer : int
        etch layer.

    '''

    size=LayoutParamInterface()
    metalized=LayoutParamInterface()
    etch_choice=LayoutParamInterface(True,False)
    etch_x=LayoutParamInterface()
    x_offset=LayoutParamInterface()
    layer=LayoutParamInterface()
    etch_layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.size=LayoutDefault.Anchorsize
        self.metalized=LayoutDefault.Anchor_metalized
        self.etch_choice=LayoutDefault.Anchoretch_choice
        self.etch_x=LayoutDefault.Anchoretch_x
        self.x_offset=LayoutDefault.Anchorx_offset
        self.layer=LayoutDefault.Anchorlayer
        self.etch_layer=LayoutDefault.Anchoretch_layer

    def draw(self):

        self._check_anchor()

        anchor=self._draw_metalized()

        etch_size=Point(
        (self.etch_x-self.size.x)/2,
        self.size.y)

        offset=Point(self.x_offset,0)

        cell=Device(self.name)

        etch_sx=pg.rectangle(
            size=(etch_size-offset).coord,
            layer=self.etch_layer)

        etch_dx=pg.rectangle(
            size=(etch_size+offset).coord,
            layer=self.etch_layer)

        etch_sx_ref=(cell<<etch_sx).move(
        destination=(Point(0,self.etch_margin.y)).coord)

        # anchor_transl=Point(etch_sx.size[0]+self.etch_margin.x,-2*self.etch_margin.y)

        anchor_transl=Point(etch_sx.xsize+self.etch_margin.x,0)

        anchor_ref=(cell<<anchor).move(
            destination=anchor_transl.coord)

        etchdx_transl=anchor_transl+Point(anchor.xsize+self.etch_margin.x,self.etch_margin.y)

        etch_dx_ref=(cell<<etch_dx).move(
            destination=etchdx_transl.coord)

        pt._copy_ports(anchor_ref,cell)

        if self.etch_choice==True:

            cell.absorb(etch_sx_ref)
            cell.absorb(anchor_ref)
            cell.absorb(etch_dx_ref)

        else:

            cell.remove(etch_sx_ref)
            cell.remove(etch_dx_ref)

        return cell

    def _draw_metalized(self):

        cell=pg.rectangle(
            size=(self.size-Point(2*self.etch_margin.x,-2*self.etch_margin.y)).coord,\
            layer=self.layer)

        [_,_,_,_,_,n,*_]=pt._get_corners(cell)

        cell.add_port(name='conn',midpoint=n.coord,width=cell.xsize,orientation=90)

        return cell

    @property
    def resistance_squares(self):

        return 2*self.metalized.y/self.metalized.x

    @property
    def etch_margin(self):

        return Point((self.size.x-self.metalized.x)/2,\
            (self.metalized.y-self.size.y)/2)

    def _check_anchor(self):

        if self.metalized.x>=self.size.x:

            # warnings.warn(f"""Metalized X capped to {self.size.x*0.9 :.2f}\n""")
            self.metalized=Point(self.size.x*0.9,self.metalized.y)

        if self.metalized.y<=self.size.y:

            # warnings.warn(f"""Metalized Y capped to {self.size.y*1.1 : .2f}""")
            self.metalized=Point(self.metalized.x,self.size.y*1.1)

class MultiAnchor(Anchor):
    ''' Anchor with multiple anchor points,equally spaced.

    Attributes
    ----------
        n : int

        spacing : pt.Point.

    '''
    n =LayoutParamInterface()

    spacing=LayoutParamInterface()

    def __init__(self,n=1,*a,**kw):

        super().__init__(*a,**kw)

        self.n=LayoutDefault.MultiAnchorn

        self.spacing=pt.Point(self.size.x/3,0)

    def _draw_metalized(self):

        import pdb; pdb.set_trace()

        metalized=super()._draw_metalized()

        metalized_all=pt.draw_array(
            metalized,x=self.n,y=1,
            row_spacing=self.spacing.y,column_spacing=self.spacing.x)

        return metalized_all

    def draw(self):

        return Anchor.draw.__wrapped__(self)

class Via(LayoutPart):
    ''' Generates via pattern.

    Derived from LayoutPart.

    Attributes
    ----------
    size : float
        if shape is 'square', side of square
        if shape is 'circle', diameter of cirlce

    shape : str (only 'square' or 'circle')
        via shape
    layer : int
        via layer.
    '''

    size=LayoutParamInterface()

    shape=LayoutParamInterface('square','circle')

    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=LayoutDefault.Vialayer
        self.shape=LayoutDefault.Viashape
        self.size=LayoutDefault.Viasize
        self.conn_layer=(LayoutDefault.layerTop,LayoutDefault.layerBottom)

    def draw(self):

        if self.shape=='square':

            cell=pg.rectangle(size=(self.size,self.size),\
                layer=self.layer)

        elif self.shape=='circle':

            cell=pg.circle(radius=self.size/2,\
            layer=self.layer)

        else:

            raise ValueError("Via shape can be \'square\' or \'circle\'")

        cell.move(origin=(0,0),\
            destination=self.origin.coord)

        cell.add_port(Port(name='conn',\
        midpoint=cell.center,\
        width=cell.xmax-cell.xmin,\
        orientation=90))

        return cell

class GSProbe(LayoutPart):
    ''' Generates GS pattern.

    Derived from LayoutPart.

    Attributes
    ----------
    size : PyResLayout.Point

    pitch : float
        probe pitch

    layer : int
        via layer.
    '''

    pitch=LayoutParamInterface()
    size=LayoutParamInterface()

    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=LayoutDefault.GSProbelayer
        self.pitch=LayoutDefault.GSProbepitch
        self.size=copy(LayoutDefault.GSProbesize)

    def draw(self):

        name=self.name

        pad_x=self.size.x

        if pad_x>self.pitch*2/3:

            pad_x=self.pitch*2/3

            # warnings.warn("Pad size too large, capped to pitch*2/3")

        pad_cell=pg.rectangle(size=(pad_x,self.size.y),\
        layer=self.layer)

        cell=Device(self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell

        cell.add_port(Port(name='gnd_left',
        midpoint=Point(pad_x/2+self.pitch,self.size.y).coord,
        width=pad_x,
        orientation=90))

        cell.add_port(Port(name='sig',
        midpoint=Point(pad_x/2,self.size.y).coord,
        width=pad_x,
        orientation=90))

        return cell

class GSGProbe(LayoutPart):
    ''' Generates GSG pattern.

    Derived from LayoutPart.

    Attributes
    ----------
    size : PyResLayout.Point

    pitch : float
        probe pitch

    layer : int
        via layer.
    '''

    pitch=LayoutParamInterface()
    size=LayoutParamInterface()
    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=LayoutDefault.GSGProbelayer
        self.pitch=LayoutDefault.GSGProbepitch
        self.size=copy(LayoutDefault.GSGProbesize)

        # self.__class__.draw=cached(self.__class__)(self.__class__.draw)

    def draw(self):

        name=self.name

        pad_x=self.size.x

        if pad_x>self.pitch*9/10:

            pad_x=self.pitch*9/10

            # warnings.warn("Pad size too large, capped to pitch*9/10")

        pad_cell=pg.compass(size=(pad_x,self.size.y),\
        layer=self.layer)

        cell=Device(self.name)

        dp=Point(self.pitch,0)

        pad_gnd_lx=cell.add_ref(pad_cell,alias='GroundLX')

        pad_sig=cell.add_ref(pad_cell,alias='Sig')
        pad_sig.move(destination=dp.coord)

        pad_gnd_rx=cell.add_ref(pad_cell,alias='GroundRX')
        pad_gnd_rx.move(destination=(2*dp).coord)

        pt._copy_ports(pad_sig,cell,prefix='Sig')
        pt._copy_ports(pad_gnd_rx,cell,prefix='GroundRX')
        pt._copy_ports(pad_gnd_lx,cell,prefix='GroundLX')
        # cell.add_port(port=pad_sig.ports['N'],name='sig')
        #
        # cell.add_port(port=pad_gnd_sx.ports['N'],name='gnd_left')
        #
        # cell.add_port(port=pad_gnd_dx.ports['N'],name='gnd_right')

        return cell

class Pad(LayoutPart):
    ''' Generates Pad geometry.

    Derived from LayoutPart.

    Attributes
    ----------
    size : float
        pad square side

    distance : float
        distance between pad edge and port

    port : phidl.Port

        port to connect pad to

    layer : int
        via layer.
    '''

    size=LayoutParamInterface()

    distance=LayoutParamInterface()

    layer=LayoutParamInterface()

    port=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.size=LayoutDefault.Padsize
        self.layer=LayoutDefault.Padlayer
        self.distance=copy(LayoutDefault.Paddistance)
        self.port=LayoutDefault.Padport

    def draw(self):

        r1=pg.compass(size=(self.port.width,self.distance),\
            layer=self.layer)

        north_port=r1.ports['N']
        south_port=r1.ports['S']

        r2=pg.compass(size=(self.size,self.size),\
            layer=self.layer)

        sq_ref=r1<<r2

        sq_ref.connect(r2.ports['S'],
            destination=north_port)

        r1.absorb(sq_ref)
        r1=join(r1)
        r1.add_port(port=south_port,name='conn')

        del r2

        return r1

    @property
    def resistance_squares(self):

        return 1+self.distance/self.port.width

class MultiLayerPad(Pad):

    __pad_base=Pad()

    def __init__(self,*a,**k):

        LayoutPart.__init__(self,*a,**k)

        self.size=LayoutDefault.Padsize

        self.distance=copy(LayoutDefault.Paddistance)

        self.port=LayoutDefault.Padport

        self.layer=(LayoutDefault.layerTop,
                   LayoutDefault.layerBottom)

    def draw(self):

        cell=pg.Device(self.name)

        pars=self.get_params()

        pars.pop("Layer")

        p=self.__pad_base

        p.set_params(pars)

        for layer in self.layer:

            p.layer=layer

            cell.absorb(cell<<p.draw())

        cell.add_port(p.draw().ports['conn'])

        return cell

class ViaInPad(MultiLayerPad):

    def draw(self):

        from pirel.modifiers import add_vias

        cell=pg.deepcopy(super().draw())

        add_vias(cell,cell.bbox,self.via,self.via.size*2,self.via.size)

        return cell

    @staticmethod
    def get_components():

        return {"Via":Via}

class LFERes(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self._stretch_top_margin=False

        LFERes._set_relations(self)

    def draw(self):

        LFERes._set_relations(self)

        idt_cell=self.idt.draw()

        cell=Device(self.name)

        idt_ref=cell.add_ref(idt_cell,alias="IDT")

        idt_top_port=idt_ref.ports['top']

        idt_bottom_port=idt_ref.ports['bottom']

        bus_cell = self.bus.draw()

        bus_ref= cell.add_ref(bus_cell,alias="BUS")

        bus_ref.connect(port=bus_cell.ports['conn'],\
        destination=idt_bottom_port)

        etch_cell=self.etchpit.draw()

        etch_ref=cell.add_ref(etch_cell,alias='EtchPit')

        etch_ref.connect(etch_ref.ports['bottom'],\
        destination=idt_ref.ports['bottom'],\
        overlap=-self.bus.size.y-self.anchor.etch_margin.y)

        anchor_cell=self.anchor.draw()

        anchor_bottom=cell.add_ref(anchor_cell,alias='AnchorBottom')

        anchor_bottom.connect(anchor_bottom.ports['conn'],
        destination=idt_ref.ports['bottom'],overlap=-self.bus.size.y)

        if not self._stretch_top_margin:

            anchor_top=cell.add_ref(anchor_cell,alias='AnchorTop')

        else:

            anchor_top_dev=deepcopy(self.anchor)

            anchor_top_dev.metalized=Point(anchor_top_dev.size.x-2,anchor_top_dev.metalized.y)

            anchor_top=cell.add_ref(anchor_top_dev.draw(),alias='AnchorTop')

            del anchor_top_dev

        anchor_top.connect(anchor_top.ports['conn'],\
            idt_ref.ports['top'],overlap=-self.bus.size.y)

        outport_top=anchor_top.ports['conn']

        outport_bottom=anchor_bottom.ports['conn']

        outport_top.name='top'
        outport_top.orientation=90
        outport_bottom.name='bottom'
        outport_bottom.orientation=-90

        outport_top.midpoint=(\
            outport_top.x,\
            outport_top.y+self.anchor.metalized.y)
        outport_bottom.midpoint=(\
            outport_bottom.x,\
            outport_bottom.y-self.anchor.metalized.y)

        cell.add_port(outport_top)
        cell.add_port(outport_bottom)

        del idt_cell,bus_cell,etch_cell,anchor_cell

        return cell

    def get_params(self):

        LFERes._set_relations(self)

        t=super().get_params()

        pop_all_dict(t,["IDT"+x for x in ["Name"]])

        pop_all_dict(t, ["Bus"+x for x in ['Name','DistanceX','DistanceY','SizeX']])

        pop_all_dict(t,["EtchPit"+x for x in['Name','ActiveAreaX','ActiveAreaY']])

        pop_all_dict(t,["Anchor"+x for x in ['Name','EtchX','XOffset','EtchChoice']])

        return t

    def _set_params(self,df):

        super()._set_params(df)

        LFERes._set_relations(self)

    def _set_relations(self):

        self.bus.size=Point(\
            self.idt.active_area.x-\
            2*self.idt.active_area_margin-\
            self.idt.pitch*(1-self.idt.coverage),\
            self.bus.size.y)

        self.bus.distance=Point(\
            0,self.idt.active_area.y+self.bus.size.y)

        self.bus.layer=self.idt.layer

        self.etchpit.active_area=Point(self.idt.active_area.x,\
            self.idt.active_area.y+2*self.bus.size.y+self.anchor.etch_margin.y*2)

        self.anchor.etch_x=self.etchpit.x*2+self.etchpit.active_area.x

        self.anchor.layer=self.idt.layer

        # if self.anchor.metalized.x>self.bus.size.x:
        #
        #     warnings.warn(f"Anchor metalized X reduced to {self.bus.size.x}")
        #
        #     self.anchor.metalized=Point(\
        #         self.bus.size.x,\
        #         self.anchor.metalized.y)

    @property
    def resistance_squares(self):

        LFERes._set_relations(self)

        ridt=self.idt.resistance_squares
        rbus=self.bus.resistance_squares
        ranchor=self.anchor.resistance_squares

        return ridt+rbus+ranchor

    def export_all(self):

        df=super().export_all()

        df["IDTResistance"]=self.idt.resistance_squares
        df["AnchorResistance"]=self.anchor.resistance_squares
        df["BusResistance"]=self.idt.resistance_squares

        return df

    @property
    def area_aspect_ratio(self):

        LFERes._set_relations(self)

        width=cell.xsize-2*self.etchpit.x

        height=cell.ysize-self.anchor.etch_margin.y-2*self.anchor.size.y

        return height/width

    @staticmethod
    def get_components():

        return {'IDT':IDT,"Bus":Bus,"EtchPit":EtchPit,"Anchor":Anchor}

class FBERes(LFERes):
    ''' Floating Bottom Electrode Resonator.

        Attributes
        ----------

            plate_position
                can be 'in(/out), short(/long)' such that
                    if 'in', plate is below active region only,
                    if 'out', plate is below bus too.

                    if 'short' plate is narrower than trench,
                    if 'long', plate is larger than the trench.

        '''
    plate_position=LayoutParamInterface(
        'in, short','out, short','in, long','out, long')

    plate_layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.plate_position='out, short'

        self.plate_layer=LayoutDefault.FBEResplatelayer

    def draw(self):

        cell=Device()

        cell.name=self.name

        supercell=LFERes.draw(self)

        super_ref=cell.add_ref(supercell,alias='LFERes')

        if self.plate_position=='out, short':

            plate=pg.rectangle(size=(self.etchpit.active_area.x+8*self.idt.active_area_margin,self.idt.length-self.idt.y_offset/2),\
            layer=self.plate_layer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            transl_rel=Point(self.etchpit.x-4*self.idt.active_area_margin,self.anchor.size.y+2*self.anchor.etch_margin.y+self.bus.size.y\
                +self.idt.y_offset*3/4)

            lr_cell=pt._get_corners(cell)[0]
            lr_plate=pt._get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate.coord,\
            destination=(lr_plate+lr_cell+transl_rel).coord)

            cell.absorb(plate_ref)

            del plate

        elif self.plate_position=='in, short':

            plate=pg.rectangle(\
                size=(\
                    self.etchpit.active_area.x-\
                        2*self.idt.active_area_margin,\
                        self.idt.length-self.idt.y_offset/2),\
                layer=self.plate_layer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            transl_rel=Point(self.etchpit.x+\
                    self.idt.active_area_margin,\
                self.anchor.size.y+\
                2*self.anchor.etch_margin.y+\
                self.bus.size.y+\
                self.idt.y_offset*3/4)

            lr_cell=pt._get_corners(cell)[0]
            lr_plate=pt._get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate.coord,\
            destination=(lr_plate+lr_cell+transl_rel).coord)

            cell.absorb(plate_ref)

            del plate

        elif self.plate_position=='out, long':

            plate=pg.rectangle(\
                size=(self.etchpit.active_area.x+\
                        8*self.idt.active_area_margin,\
                    self.idt.length+\
                        2*self.bus.size.y+\
                        self.idt.y_offset),\
                layer=self.plate_layer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            transl_rel=Point(self.etchpit.x-\
                4*self.idt.active_area_margin,\
                    self.anchor.size.y+2*self.anchor.etch_margin.y)

            lr_cell=pt._get_corners(cell)[0]
            lr_plate=pt._get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate.coord,\
            destination=(lr_plate+lr_cell+transl_rel).coord)

            cell.absorb(plate_ref)

            del plate

        elif self.plate_position=='in, long':

            plate=pg.rectangle(\
                size=(\
                    self.etchpit.active_area.x-\
                        2*self.idt.active_area_margin,\
                        self.idt.length+\
                            2*self.bus.size.y+\
                            self.idt.y_offset),
                layer=self.plate_layer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            transl_rel=Point(self.etchpit.x+\
                    self.idt.active_area_margin,\
                        self.anchor.size.y+2*self.anchor.etch_margin.y)

            lr_cell=pt._get_corners(cell)[0]
            lr_plate=pt._get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate.coord,\
            destination=(lr_plate+lr_cell+transl_rel).coord)

            cell.absorb(plate_ref)

            del plate

        pt._copy_ports(supercell,cell)

        return cell

class TwoPortRes(FBERes):

    def __init__(self,*a,**k):

        super().__init__(*a,**k)

        self.plate_position='in, long'

        self.plate_layer=LayoutDefault.layerBottom

    def draw(self):

        cell=Device()

        cell.name=self.name

        supercell=FBERes.draw(self)

        super_ref=cell.add_ref(supercell,alias='FBERes')

        lfe_cell=supercell['LFERes'].parent

        for label in ('AnchorBottom','AnchorTop'):

            anchor_ref=lfe_cell[label]

            anchor_metal=cell.add_polygon(
                anchor_ref.get_polygons(
                    by_spec=(self.idt.layer,0)),
                layer=self.plate_layer)

        pt._copy_ports(supercell,cell)

        self._make_ground_connections(cell)

        return cell

    def _make_ground_connections(self,cell):

        [ll,lr,ul,ur,c,n,s,w,e]=pt._get_corners(cell)

        margin=pt.Point(self.anchor.size.x-self.anchor.metalized.x,0)

        cell.add_port(
            name='GroundLX',
            midpoint=(w-margin).coord,
            width=ul.y-ll.y,
            orientation=180)

        cell.add_port(
            name='GroundRX',
            midpoint=(e+margin).coord,
            width=ur.y-lr.y,
            orientation=0)

        ground_port_lx=cell.ports["GroundLX"]
        ground_port_rx=cell.ports["GroundRX"]

        for corner,sig,tag in zip([ll,lr,ul,ur],[-1,1,-1,1],['bottom','bottom','top','top']):

            conn_width=cell.ports[tag].width

            if tag=='top':
                orient=90
            elif tag=='bottom':
                orient=270

            conn_port=Port(
                width=conn_width,
                midpoint=(corner+sig*pt.Point(conn_width/2,0)+sig*margin).coord,
                orientation=orient)

            r=Routing()
            r.layer=(self.plate_layer,)
            r.source=cell.ports[tag]
            r.destination=conn_port
            r.overhang=conn_width
            cell.add(r.draw())

class TFERes(LFERes):

    bottom_layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.bottom_layer=LayoutDefault.layerBottom

    def draw(self):

        lfe_cell=LFERes.draw(self)

        cell=Device(name=self.name)

        cell.add_ref(lfe_cell,alias='TopCell')

        idt_bottom=deepcopy(self.idt)

        idt_bottom.layer=self.bottom_layer

        idt_bottom.y_offset=-idt_bottom.y_offset

        idt_ref=cell.add_ref(idt_bottom.draw(),alias='BottomIDT')

        idt_ref.move(destination=(0,-idt_bottom.y_offset))

        bus_bottom=deepcopy(self.bus)

        bus_bottom.layer=self.bottom_layer

        bus_ref=cell.add_ref(bus_bottom.draw(),alias='BottomBus')

        bus_ref.move(origin=(0,0),\
        destination=(0,-self.bus.size.y))

        anchor_bottom=deepcopy(self.anchor)

        anchor_bottom.layer=self.bottom_layer

        anchor_bottom.etch_choice=False

        anchor_ref=cell.add_ref(anchor_bottom.draw(),alias="BottomAnchor_Top")

        anchor_ref.connect(anchor_ref.ports['conn'],
            destination=cell['TopCell'].ports['top'])

        anchor_ref.rotate(center=anchor_ref.ports['conn'].midpoint,angle=180)

        anchor_ref_2=cell.add_ref(anchor_bottom.draw(),alias="BottomAnchor_Top")

        anchor_ref_2.connect(anchor_ref_2.ports['conn'],
            destination=cell['TopCell'].ports['bottom'])

        anchor_ref_2.rotate(center=anchor_ref_2.ports['conn'].midpoint,angle=180)

        pt._copy_ports(lfe_cell,cell)

        return cell

class SMD(LayoutPart):
    ''' Generate pad landing for SMD one-port component

    Attributes
    ----------
    layer : int
        metal layer

    size : pt.Point

    distance :pt.Point.
    '''

    layer=LayoutParamInterface()

    size=LayoutParamInterface()

    distance=LayoutParamInterface()

    def __init__(self,*a,**kw):

        super().__init__(*a,**kw)
        self.layer=LayoutDefault.SMDLayer
        self.distance=LayoutDefault.SMDDistance
        self.size=LayoutDefault.SMDSize

    def draw(self):

        unit_pad=Device()

        for l in self.layer:

            unit_pad.add_ref(pg.compass(size=self.size.coord,layer=l),alias='layer'+str(l))

        cell=Device(name=self.name)

        pt._copy_ports(pg.compass(size=self.size.coord,layer=l),unit_pad)

        p1=cell.add_ref(unit_pad,alias='Pad_1')
        p2=cell.add_ref(unit_pad,alias='Pad_2')

        p2.move(destination=self.distance.coord)

        pt._copy_ports(p1,cell,suffix='_1')
        pt._copy_ports(p2,cell,suffix='_2')

        return cell

    def set_01005(self):

        self.size=pt.Point(300,250)

        self.distance=pt.Point(0,400)

class Routing(LayoutPart):
    ''' Generate automatic routing connection

    Derived from LayoutPart.

    Attributes
    ----------
    clearance : iterable of two coordinates
        bbox of the obstacle

    source: phidl.Port

    overhang: float
        distance to extend port in its direction before routing

    destination: phidl.Port

    layer : int
        metal layer.

    side : str (can be "auto","left","right")
        where to go if there is an obstacle.
        decides where to go if there is an obstacle in the routing,
        only 'auto','left','right'.
    '''

    _radius=0.1

    _num_pts=30

    _tol=1e-3

    _simplification=1

    clearance=LayoutParamInterface()

    overhang=LayoutParamInterface()

    side=LayoutParamInterface('left','right','auto')

    source=LayoutParamInterface()

    destination=LayoutParamInterface()

    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.clearance=LayoutDefault.Routingclearance
        self.side=LayoutDefault.Routingside
        self.source=LayoutDefault.Routingports[0]
        self.destination=LayoutDefault.Routingports[1]
        self.layer=LayoutDefault.Routinglayer
        self.overhang=LayoutDefault.Routingoverhang
        self._auto_overhang=False

    def _check_frame(self):

        cell=self._draw_frame()

        check(cell)

    def _draw_frame(self):

        frame=Device()

        for l in self.layer:

            frame<<pg.bbox(self.clearance,layer=l)

        frame.add_port(self.source)

        frame.add_port(self.destination)

        return frame

    def draw(self):

        p=self.path

        path_cell=self._make_path_cell(p,self.source,self.destination)

        path_cell.name=self.name

        return path_cell

    def _make_path_cell(self,p,s,d):

        cell=Device()

        for l in self.layer:

            cell<<p.extrude(
                layer=l,
                width=[s.width,d.width],
                simplify=self._simplification)

        return join(cell)

    @property
    def path(self):

        s=self.source

        d=self.destination

        if self._auto_overhang:

            self.overhang=self._calculate_overhang(s,d)

        if Point(s.midpoint).in_box(self.clearance) :

            raise ValueError(f" Source of routing {s.midpoint} is in clearance area {self.clearance}")

        if Point(d.midpoint).in_box(self.clearance):
            # import pdb; pdb.set_trace()
            # Point(d.midpoint).in_box(self.clearance)
            raise ValueError(f" Destination of routing {d.midpoint} is in clearance area{self.clearance}")

        try:

            p=self._draw_non_hindered_path(s,d)

        except Exception as e_non_hind:

                p=self._draw_hindered_path(s,d,self.side)

        return p

    def _draw_with_frame(self):

        cell_frame=self._draw_frame()

        cell_frame.absorb(cell_frame<<self.draw())

        return cell_frame

    def _draw_non_hindered_path(self,s,d):

        p1=Point(s.midpoint)

        p2=Point(d.midpoint)

        dt1_norm=Point(s.normal[1])-Point(s.normal[0])

        p1_proj=p1+dt1_norm*self.overhang

        dt2_norm=Point(d.normal[1])-Point(d.normal[0])

        p2_proj=p2+dt2_norm*self.overhang

        p=self._make_path(p1,p1_proj,p2_proj,p2)

        if not self._is_hindered(p,s,d):

            return p

        else:

            raise ValueError("path is hindered")

        for p_mid in (Point(p1_proj.x,p2_proj.y),Point(p2_proj.x,p1_proj.y)):

            try:

                p=self._make_path(p1,p1_proj,p_mid,p2_proj,p2)

                if not self._is_hindered(p):

                    return p

            except :

                pass

        else:

            raise ValueError("path is hindered")

    def _draw_hindered_path(self,s,d,side='auto'):

        ll,lr,ul,ur,*_=pt._get_corners(pg.bbox(self.clearance))

        extra_width=self._get_max_width()

        if side=='auto':

            path1=self._draw_hindered_path(s,d,'left')

            path2=self._draw_hindered_path(s,d,'right')

            if path2.length()<path1.length() : return path2

            else : return path1

        p1=Point(s.midpoint)

        p2=Point(d.midpoint)

        dt1_norm=Point(s.normal[1])-Point(s.normal[0])

        p1_proj=p1+dt1_norm*self.overhang

        dt2_norm=Point(d.normal[1])-Point(d.normal[0])

        p2_proj=p2+dt2_norm*self.overhang

        if side=='left':

            p_below_clearance=Point(ll.x-extra_width,p1_proj.y)

        elif side=='right':

            p_below_clearance=Point(lr.x+extra_width,p1_proj.y)

        p_above_clearance=Point(p_below_clearance.x,ur.y+(ll.y-p1_proj.y))

        p_at_dest=Point(p_below_clearance.x,p2_proj.y)

        if abs(p_at_dest-p_below_clearance)<=abs(p_above_clearance-p_below_clearance):

            p_mid2=p_at_dest

        else:

            p_mid2=p_above_clearance

        for p_mid3 in (Point(p_mid2.x,p2_proj.y),Point(p2_proj.x,p_mid2.y)):

            points=[p1,p1_proj,p_below_clearance,p_mid2,p_mid3,p2_proj,p2]

            try:

                p=self._make_path(*points)

                if not self._is_hindered(p,s,d):

                    return p

            except:

                pass

        else:

            raise ValueError("path is impossible")

    def _is_hindered(self,path,s,d):

        test_path_cell=self._make_path_cell(path,s,d)

        try:

            test_path_cell.remove_polygons(
                lambda pt,lay,dt : lay==any(self.layer[1:]))

        except:

            pass

        if self.clearance==((0,0),(0,0)):

            return False

        else:

            return not is_cell_outside(
                test_path_cell,
                pg.bbox(self.clearance,layer=self.layer[0]),
                tolerance=0)

    def _make_path(self,*points):

        sel_points=list(points)

        for p1,p2 in zip(points, points[1:]):

            if p2==p1:

                sel_points.remove(p2)

        sel_points=pt._check_points_path(*sel_points,trace_width=self._get_max_width())

        return pp.smooth(points=sel_points,radius=self._radius,num_pts=self._num_pts)

    def set_auto_overhang(self,value):
        ''' Sets automatically the routing overhead as 1/5 of distance between source and destination.

        Parameters
        ----------
            value : boolean.
        '''

        if isinstance(value,bool):
            self._auto_overhang=value
        else:
            raise ValueError("set_auto_overhang accepts True/False")

    @staticmethod
    def _calculate_overhang(s,d):

        p1=Point(s.midpoint)
        p2=Point(d.midpoint)

        dist=abs(p2-p1)

        return dist/5

    @property
    def resistance_squares(self):

        return self.path.length()/self._get_max_width()

    def _get_max_width(self):
        return max(self.source.width,self.destination.width)

class MultiRouting(Routing):
    ''' Handles routings on multiple ports.

    Attributes
    ----------
    source: tuple of phidl.Port

    destination: tuple of phidl.Port

    '''
    def __init__(self,*a,**k):

        LayoutPart.__init__(self,*a,**k)

        self.source=LayoutDefault.MultiRoutingsources
        self.destination=LayoutDefault.MultiRoutingdestinations
        self.clearance=LayoutDefault.Routingclearance
        self.layer=LayoutDefault.Routinglayer
        self.side=LayoutDefault.Routingside
        self.overhang=LayoutDefault.Routingoverhang
        self._auto_overhang=False

    @property
    def path(self):

        p=[]

        for s in self.source:

            for d in self.destination:

                r=self._make_routing(s,d)

                p.append(r.path)

        return p

    def _make_routing(self,s,d):

        r=Routing()

        r.clearance=self.clearance

        r.side=self.side

        r.layer=self.layer

        r.source=s

        r.destination=d

        r.overhang=self.overhang

        if self._auto_overhang:

            r.set_auto_overhang(True)

        return r

    def _draw_frame(self):

        frame=Device()

        for l in self.layer:

            frame<<pg.bbox(self.clearance,layer=l)

        for s in self.source:

            frame.add_port(s)

        for d in self.destination:

            frame.add_port(d)

        return frame

    def draw(self):

        c=Device(name=self.name)

        for s in self.source:

            for d in self.destination:

                r=self._make_routing(s,d)
                c<<self._make_path_cell(r.path,s,d)

        return c

    @property
    def resistance_squares(self):

        resistance=[]

        for p,q in zip(self.path,self._get_max_width()):

            resistance.append(p.length()/q)

        return resistance

    def _get_max_width():

        width=[]

        for s in self.source:

            for d in self.destination:

                r=self._make_routing(s,d)

                width.append(r._get_max_width())

        return width

class ParasiticAwareMultiRouting(MultiRouting):

    @property
    def path(self):

        numports=len(self.destination)

        if numports == 1 or numports == 2 :

            return super().path

        else :

            p=[]

            if numports %2 == 0:

                midport=int(numports/2)

                base_routing=deepcopy(self)

                base_routing.destination=tuple(self.destination[midport-1:midport+1])

                for dest,nextdest in zip(self.destination,self.destination[1:]):

                    if dest in base_routing.destination :

                        if nextdest in base_routing.destination:

                            p.extend(base_routing.path)

                        else:

                            p.append(self._draw_non_hindered_path(dest,nextdest))

                    else:

                        p.append(self._draw_non_hindered_path(dest,nextdest))

                return p

            elif numports %2 == 1:

                midport=int((numports-1)/2)

                base_routing=deepcopy(self)

                base_routing.destination=(self.destination[midport],)

                for dest,nextdest in zip(self.destination,self.destination[1:]):

                    if dest in base_routing.destination :

                        p.extend(base_routing.path)

                        p.append(self._draw_non_hindered_path(dest,nextdest))

                    else:

                        p.append(self._draw_non_hindered_path(dest,nextdest))

                return p

    def _make_paware_connection(self,s,d):

        p1=Point(s.midpoint)

        p2=Point(d.midpoint)

        p1=p0+Point(0,self.overhang)

        p2=Point(d.midpoint[0],p1.y)

        p3=Point(p2.x,d.midpoint[1])

        return self._make_path(p0,p1,p2,p3)

    @property
    def resistance_squares(self):

        p=self.path

        numpaths=len(p)

        if numpaths==1 or numpaths==2:

            return super().resistance_squares

        else:

            original_res=super().resistance_squares

            res=[]

            if numpaths%2==0:

                midpoint=int(numpaths/2)

                for x in range(numpaths):

                    if x==midpoint-1 or x==midpoint:

                        res.append(original_res[x])

                    else:

                        res.append(original_res[x]-self._yovertravel(self.destination[x])/self._get_max_width()[x])

                return res

            if numpaths%2==1:

                midpoint=int((numpaths-1)/2)

                for x in range(numpaths):

                    if x==midpoint:

                        res.append(original_res[x])

                    else:

                        res.append(original_res[x]-self._yovertravel(self.destination[x])/self.trace_width)

                return res

_allclasses=(Text,IDT,PartialEtchIDT,Bus,EtchPit,Anchor,MultiAnchor,Via,Routing,GSProbe,GSGProbe,
Pad,MultiLayerPad,ViaInPad,LFERes,FBERes,TwoPortRes,TFERes,MultiRouting,ParasiticAwareMultiRouting)

for cls in _allclasses:

    cls.draw=pirel_cache(cls.draw)

    cls() # to init _params_dict

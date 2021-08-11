from pirel.tools import *

from pirel.tools import _check_points_path

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

class TextParam:
    ''' Class to store text data and to add it in cells.

    It controls how the text labels generated are formatted.
    You can add text to a cell using the add_text() method.

    Attributes
    ----------
    font : string
            if overridden, needs to be in sketch/ path

    size : float

    location : 'left','right','top','bottom'

    distance :  PyResLayout.Point

    label :     string
        can be multiline if '\\n' is added

    layer:   int.
    '''

    _valid_names={'font','size','location','distance','label','layer'}

    _msg_err="""Invalid key for text_param.
    Valid options are :{}""".format("\n".join(_valid_names))

    _default=LayoutDefault.TextParams

    def __init__(self,df={}):

        '''Initialize TextParam.

        If no value is passed, default values are used (from LayoutDefault class).

        Parameters
        ----------
            df : dict (optional)
                key:value of all the attributes.
        '''
        if not isinstance(df,dict):

            raise ValueError("text params is initialized by a dict")

        else:

            for key,value in df.items():

                self.set(key,value)

    def set(self,key,value):

        if not key in self._valid_names:

            raise ValueError(self._msg_err)

        else:

            setattr(self,key,value)

    def get(self,key):

        if not key in self._valid_names:

            raise ValueError(self._msg_err)

        if hasattr(self,key):

            return getattr(self,key)

        else:

            return self._default[key]

    def __call__(self,df={}):

        if not isinstance(df,dict):

            raise ValueError("Update textparam with a dict")

        for key,value in df.items():

            self.set(key,value)

        ret_dict={}

        for name in self._valid_names:

            ret_dict[name]=self.get(name)

        return rect_dict

    def add_text(self,cell,label=None):
        '''Add text to a cell.

        Parameters
        ---------

        cell : phidl.Device

        Returns
        -------

        cell :phidl.Device.
        '''

        if label is not None:

            if isinstance(label,str):

                self.set('label',label)

            else:

                raise ValueError("Passed parameter {} is not a string ".format(label.__class__.__name__))

        text_cell=DeviceReference(self.draw())

        o=Point(0,0)

        ll,lr,ul,ur=get_corners(cell)

        text_location=self.get('location')

        text_size=Point(text_cell.size)

        text_distance=self.get('distance')

        if text_location=='top':

            o=Point((ul.x+ur.x)/2,ul.y)-Point(text_size.x/2,0)+text_distance

        elif text_location=='bottom':

            o=Point((ll.x+lr.x)/2,ll.y)-Point(text_size.x/2,text_size.y)-text_distance

        elif text_location=='right':

            o=ur+text_distance

            text_cell.rotate(angle=-90)

        elif text_location=='left':

            o=ll-text_distance

            text_cell.rotate(angle=90)

        cell.add(text_cell)

        text_cell.move(origin=(0,0),\
            destination=o.coord)

        return cell

    def __str__(self):

        dict=self()

        return pd.Series(dict).to_string()

    def draw(self):

        text_opts={}

        for name in self._valid_names:

            text_opts[name]=self.get(name)

        package_directory = str(pathlib.Path(__file__).parent/'addOns')

        font=os.path.join(package_directory,text_opts['font'])

        text_cell=pg.text(size=text_opts['size'],\
            text=text_opts['label'],\
            font=font,\
            layer=text_opts['layer'])

        return text_cell

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

        cell.add_port(Port(name='top',\
        midpoint=(self.origin+\
        Point(midx,self.length+self.y_offset)).coord,\
        width=totx,
        orientation=90))

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

        return Point(0,self.active_area.x/2)

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

        o=self.origin

        rect=pg.rectangle(size=(self.coverage*self.pitch,self.length),\
            layer=self.layer)

        rect.move(origin=(0,0),destination=o.coord)

        unitcell=Device()

        r1=unitcell << rect

        unitcell.absorb(r1)

        r2 = unitcell << rect

        r2.move(origin=o.coord,\
        destination=(o+Point(self.pitch,self.y_offset)).coord)

        r3= unitcell<< rect

        r3.move(origin=o.coord,\
            destination=(o+Point(2*self.pitch,0)).coord)

        unitcell.absorb(r2)

        unitcell.absorb(r3)

        unitcell.name="UnitCell"

        del rect

        return unitcell

class PartialEtchIDT(IDT):

    def _draw_unit_cell(self):

        o=self.origin

        rect=pg.rectangle(size=(self.coverage*self.pitch,self.length),
            layer=self.layer)

        rect.move(origin=(0,0),destination=o.coord)

        unitcell=Device()

        r1=unitcell << rect

        unitcell.absorb(r1)

        rect_partialetch=pg.rectangle(
            size=(
                (1-self.coverage)*self.pitch,self.length-self.y_offset),
            layer=LayoutDefault.layerPartialEtch)

        rect_partialetch.move(origin=o.coord,
            destination=(self.pitch*self.coverage,self.y_offset))

        rp1=unitcell<<rect_partialetch

        rp2=unitcell<<rect_partialetch

        rp2.move(destination=(self.pitch,0))

        r2 = unitcell << rect

        r2.move(origin=o.coord,
        destination=(o+Point(self.pitch,self.y_offset)).coord)

        r3= unitcell<< rect

        r3.move(origin=o.coord,\
            destination=(o+Point(2*self.pitch,0)).coord)

        rect_partialetch_side=pg.rectangle(
            size=(
                (1-self.coverage)*self.pitch/2,self.length-self.y_offset),
            layer=LayoutDefault.layerPartialEtch)

        petch_side1=unitcell<<rect_partialetch_side

        petch_side2=unitcell<<rect_partialetch_side

        petch_side1.move(origin=o.coord,
            destination=(-petch_side1.xsize,self.y_offset))

        petch_side2.move(origin=o.coord,
            destination=(self.pitch*2+self.pitch*self.coverage,self.y_offset))

        unitcell.absorb(r2)

        unitcell.absorb(r3)

        unitcell.absorb(petch_side1)

        unitcell.absorb(petch_side2)

        unitcell.name="UnitCell"

        del rect,rect_partialetch

        return unitcell

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
        o=self.origin

        pad=pg.rectangle(size=self.size.coord,\
        layer=self.layer).move(origin=(0,0),\
        destination=o.coord)

        cell=Device(self.name)

        r1=cell<<pad
        cell.absorb(r1)
        r2=cell <<pad

        r2.move(origin=o.coord,\
        destination=(o+self.distance).coord)

        cell.absorb(r2)

        cell.add_port(name='conn',\
        midpoint=(o+Point(self.size.x/2,self.size.y)).coord,\
        width=self.size.x,\
        orientation=90)

        del pad

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
        o=self.origin

        main=pg.rectangle(size=(self.x,self.active_area.y),
            layer=self.layer)

        main.move(destination=o.coord)

        etch=Device(self.name)

        etch_lx=etch<<main

        etch_rx=etch<<main

        etch_rx.move(destination=(self.x+self.active_area.x,0))

        port_up=Port('top',\
        midpoint=(o+Point(self.x+self.active_area.x/2,self.active_area.y)).coord,\
        width=self.active_area.x,\
        orientation=-90)

        port_down=Port('bottom',\
        midpoint=(o+Point(self.x+self.active_area.x/2,0)).coord,\
        width=self.active_area.x,\
        orientation=90)

        etch.add_port(port_up)
        etch.add_port(port_down)

        return etch

class Anchor(LayoutPart):
    ''' Generates anchor structure.

    Attributes
    ----------
    size : PyResLayout.Point
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

        self.size=copy(LayoutDefault.Anchorsize)
        self.metalized=copy(LayoutDefault.Anchor_metalized)
        self.etch_choice=LayoutDefault.Anchoretch_choice
        self.etch_x=LayoutDefault.Anchoretch_x
        self.x_offset=LayoutDefault.Anchorx_offset

        self.layer=LayoutDefault.Anchorlayer
        self.etch_layer=LayoutDefault.Anchoretch_layer

    def draw(self):
        ''' Generates layout cell based on current parameters.

        'conn' port is included in the cell.

        Returns
        -------
        cell : phidl.Device.
        '''

        self._check_anchor()

        o=self.origin

        anchor=pg.rectangle(\
            size=(self.size-Point(2*self.etch_margin.x,-2*self.etch_margin.y)).coord,\
            layer=self.layer)

        etch_size=Point(\
        (self.etch_x-self.size.x)/2,\
        self.size.y)

        offset=Point(self.x_offset,0)

        cell=Device(self.name)

        etch_sx=pg.rectangle(\
            size=(etch_size-offset).coord,\
            layer=self.etch_layer)

        etch_dx=pg.rectangle(\
            size=(etch_size+offset).coord,\
            layer=self.etch_layer)

        etch_sx_ref=(cell<<etch_sx).move(origin=(0,0),\
        destination=(o-Point(0,self.etch_margin.y)).coord)

        anchor_transl=o+Point(etch_sx.size[0]+self.etch_margin.x,-2*self.etch_margin.y)

        anchor_ref=(cell<<anchor).move(origin=(0,0),\
        destination=anchor_transl.coord)

        etchdx_transl=anchor_transl+Point(anchor.size[0]+self.etch_margin.x,+self.etch_margin.y)

        etch_dx_ref=(cell<<etch_dx).move(origin=(0,0),\
        destination=etchdx_transl.coord)

        cell.add_port(name='conn',\
        midpoint=(anchor_transl+Point(self.size.x/2-self.etch_margin.x,self.size.y+2*self.etch_margin.y)).coord,\
        width=self.metalized.x,\
        orientation=90)

        if self.etch_choice==True:

            cell.absorb(etch_sx_ref)
            cell.absorb(anchor_ref)
            cell.absorb(etch_dx_ref)

        else:

            cell.remove(etch_sx_ref)
            cell.remove(etch_dx_ref)

        del anchor, etch_sx,etch_dx

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

        o=self.origin

        pad_x=self.size.x

        if pad_x>self.pitch*2/3:

            pad_x=self.pitch*2/3

            # warnings.warn("Pad size too large, capped to pitch*2/3")

        pad_cell=pg.rectangle(size=(pad_x,self.size.y),\
        layer=self.layer)

        pad_cell.move(origin=(0,0),\
        destination=o.coord)

        cell=Device(self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell
        pad_sig.move(origin=o.coord,\
        destination=(o+dp).coord)

        cell.add_port(Port(name='gnd_left',\
        midpoint=(o+Point(pad_x/2+self.pitch,self.size.y)).coord,\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name='sig',\
        midpoint=(o+Point(pad_x/2,self.size.y)).coord,\
        width=pad_x,\
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

        o=self.origin

        pad_x=self.size.x

        if pad_x>self.pitch*9/10:

            pad_x=self.pitch*9/10

            # warnings.warn("Pad size too large, capped to pitch*9/10")

        pad_cell=pg.rectangle(size=(pad_x,self.size.y),\
        layer=self.layer)

        pad_cell.move(origin=(0,0),\
        destination=o.coord)

        cell=Device(self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell
        pad_sig.move(origin=o.coord,\
        destination=(o+dp).coord)

        pad_gnd_dx=cell<<pad_cell
        pad_gnd_dx.move(origin=o.coord,\
        destination=(o+dp*2).coord)

        cell.add_port(Port(name='sig',\
        midpoint=(o+Point(pad_x/2+self.pitch,self.size.y)).coord,\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name='gnd_left',\
        midpoint=(o+Point(pad_x/2,self.size.y)).coord,\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name='gnd_right',\
        midpoint=(o+Point(pad_x/2+2*self.pitch,self.size.y)).coord,\
        width=pad_x,\
        orientation=90))

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

class ViaInPad(Pad):

    def draw(self):

        via=self.via.draw()

        cell=pg.deepcopy(super().draw())

        viaref=cell.add_ref(via,alias="Via")

        viaref.connect('conn',destination=cell.ports['conn'])

        viaref.move(destination=(0,self.size/2+self.distance))

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
    plate_position=LayoutParamInterface(\
        'in, short','out, short','in, long','out, long')

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.plate_position='out, short'

        self.platelayer=LayoutDefault.FBEResplatelayer

    def draw(self):

        cell=Device()

        cell.name=self.name

        supercell=LFERes.draw(self)

        super_ref=cell.add_ref(supercell)

        if self.plate_position=='out, short':

            plate=pg.rectangle(size=(self.etchpit.active_area.x+8*self.idt.active_area_margin,self.idt.length-self.idt.y_offset/2),\
            layer=self.platelayer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            transl_rel=Point(self.etchpit.x-4*self.idt.active_area_margin,self.anchor.size.y+2*self.anchor.etch_margin.y+self.bus.size.y\
                +self.idt.y_offset*3/4)

            lr_cell=get_corners(cell)[0]
            lr_plate=get_corners(plate_ref)[0]

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
                layer=self.platelayer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            transl_rel=Point(self.etchpit.x+\
                    self.idt.active_area_margin,\
                self.anchor.size.y+\
                2*self.anchor.etch_margin.y+\
                self.bus.size.y+\
                self.idt.y_offset*3/4)

            lr_cell=get_corners(cell)[0]
            lr_plate=get_corners(plate_ref)[0]

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
                layer=self.platelayer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            transl_rel=Point(self.etchpit.x-\
                4*self.idt.active_area_margin,\
                    self.anchor.size.y+2*self.anchor.etch_margin.y)

            lr_cell=get_corners(cell)[0]
            lr_plate=get_corners(plate_ref)[0]

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
                layer=self.platelayer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            transl_rel=Point(self.etchpit.x+\
                    self.idt.active_area_margin,\
                        self.anchor.size.y+2*self.anchor.etch_margin.y)

            lr_cell=get_corners(cell)[0]
            lr_plate=get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate.coord,\
            destination=(lr_plate+lr_cell+transl_rel).coord)

            cell.absorb(plate_ref)

            del plate

        for name,port in supercell.ports.items():

            cell.add_port(port,name)

        return cell

class TFERes(LFERes):

    bottom_layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.bottom_layer=LayoutDefault.layerBottom

    def draw(self):

        cell=Device(name=self.name)

        lfe_cell=LFERes.draw(self)

        cell.add_ref(lfe_cell,alias='TopCell')

        idt_bottom=copy(self.idt)

        idt_bottom.layer=self.bottom_layer

        idt_ref=cell.add_ref(idt_bottom.draw(),alias='BottomIDT')

        p_bott=idt_ref.ports['bottom']

        p_bott_coord=Point(p_bott.midpoint)

        idt_ref.mirror(p1=(p_bott_coord-Point(p_bott.width/2,0)).coord,\
            p2=(p_bott_coord+Point(p_bott.width/2,0)).coord)

        idt_ref.move(origin=(idt_ref.xmin,idt_ref.ymax),\
            destination=(idt_ref.xmin,idt_ref.ymax+self.idt.length+self.idt.y_offset))

        bus_bottom=copy(self.bus)

        bus_bottom.layer=self.bottom_layer

        bus_ref=cell.add_ref(bus_bottom.draw(),alias='BottomBus')

        bus_ref.move(origin=(0,0),\
        destination=(0,-self.bus.size.y))

        anchor_bottom=copy(self.anchor)

        anchor_bottom.layer=self.bottom_layer

        anchor_bottom.etch_choice=False

        anchor_ref=cell.add_ref(anchor_bottom.draw(),alias="BottomAnchor_Top")

        anchor_ref.connect(anchor_ref.ports['conn'],\
            destination=idt_ref.ports['top'],\
            overlap=-self.bus.size.y)

        anchor_ref_2=cell.add_ref(anchor_bottom.draw(),alias="BottomAnchor_Bottom")

        anchor_ref_2.connect(anchor_ref_2.ports['conn'],\
            destination=idt_ref.ports['bottom'],\
            overlap=-self.bus.size.y)

        for p_value in lfe_cell.ports.values():

            cell.add_port(p_value)

        return cell

class Routing(LayoutPart):
    ''' Generate automatic routing connection

    Derived from LayoutPart.

    Attributes
    ----------
    clearance : iterable of two coordinates
        bbox of the obstacle

    trace_width : float
        with of routing

    source: phidl.Port

    destination: phidl.Port
        for now, the ports have to be oriented as follows:
            +90 -> -90 if below obstacle
            +90 -> +90 if above obstacle
            0 -> +90 if above obstacle
            180 -> +90 if above obstacle

    layer : int
        metal layer.

    side : str (can be "auto","left","right")

        where to go if there is an obstacle.
        decides where to go if there is an obstacle in the routing,
        only 'auto','left','right'

    '''

    _radius=0.1

    _num_pts=30

    _tol=1e-3

    clearance= LayoutParamInterface()

    side=LayoutParamInterface('left','right','auto')

    trace_width=LayoutParamInterface()

    source=LayoutParamInterface()

    destination=LayoutParamInterface()

    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.clearance=LayoutDefault.Routingclearance
        self.side=LayoutDefault.Routingside
        self.trace_width=LayoutDefault.Routingtrace_width
        self.source=LayoutDefault.Routingports[0]
        self.destination=LayoutDefault.Routingports[1]
        self.layer=LayoutDefault.Routinglayer

    def _draw_frame(self):

        rect=pg.bbox(self.clearance,layer=self.layer)
        rect.add_port(self.source)
        rect.add_port(self.destination)
        rect.name=self.name+"frame"

        return rect

    def draw(self):

        p=self.path

        x=CrossSection()

        x.add(layer=self.layer,width=self.trace_width)

        import pdb; pdb.set_trace()

        path_cell=join(x.extrude(p,simplify=0.1))

        path_cell.name=self.name

        return path_cell

    @property
    def path(self):

        bbox=pg.bbox(self.clearance)

        ll,lr,ul,ur=get_corners(bbox)

        source=self.source

        destination=self.destination

        if source.y>destination.y:

            source=copy(self.destination)

            destination=copy(self.source)

        if Point(source.midpoint).in_box(bbox.bbox) :

            raise ValueError(f" Source of routing {source.midport} is in clearance area {bbox.bbox}")

        if Point(destination.midpoint).in_box(bbox.bbox):

            raise ValueError(f" Destination of routing{destination.midpoint} is in clearance area{bbox.bbox}")

        if destination.y<=ll.y+self._tol  : # destination is below clearance

            p=self._draw_non_hindered_path(source,destination)

        else: #destination is above clearance

            if source.y>ul.y-self._tol: #source is above clearance:

                p=self._draw_non_hindered_path(source,destination)

            else: #hindered case

                if not destination.orientation==90 :

                    raise ValueError("Routing case not covered yet")

                elif source.orientation==0 : #right pad

                        source.name='source'

                        destination.name='destination'

                        p0=Point(source.midpoint)

                        p1=Point(ur.x+self.trace_width,p0.y)

                        p2=Point(p1.x,ur.y+self.trace_width)

                        p3=Point(destination.x,p2.y)

                        p4=Point(destination.x,destination.y)

                        list_points_rx=_check_points_path(p0,p1,p2,p3,p4,trace_width=self.trace_width)

                        try:

                            p=pp.smooth(points=list_points_rx,radius=self._radius,num_pts=self._num_pts)

                        except Exception :

                            raise ValueError("error in +0 source, rx path")

                if source.orientation==90 :

                    if source.x+self.trace_width>ll.x and source.x-self.trace_width<lr.x: #source tucked inside clearance

                        p0=Point(source.midpoint)

                        center_box=Point(bbox.center)

                        #left path
                        p1=p0-Point(0,source.width/2)

                        p2=Point(ll.x-self.trace_width,p1.y)

                        p3=Point(p2.x,self.trace_width+destination.y)

                        p4=Point(destination.x,p3.y)

                        p5=Point(destination.x,destination.y)

                        list_points_lx=_check_points_path(p0,p1,p2,p3,p4,p5,trace_width=self.trace_width)

                        try:

                            p_lx=pp.smooth(points=list_points_lx,radius=self._radius,num_pts=self._num_pts)

                        except:

                            raise ValueError("error in +90 hindered tucked path, lx path")

                        #right path

                        p1=p0-Point(0,source.width/2)

                        p2=Point(lr.x+self.trace_width,p1.y)

                        p3=Point(p2.x,self.trace_width+destination.y)

                        p4=Point(destination.x,p3.y)

                        p5=Point(destination.x,destination.y)

                        list_points_rx=_check_points_path(p0,p1,p2,p3,p4,p5,trace_width=self.trace_width)

                        try:

                            p_rx=pp.smooth(points=list_points_rx,radius=self._radius,num_pts=self._num_pts)

                        except:

                            raise ValueError("error in +90 source, rx path")

                        if self.side=='auto':

                            if p_lx.length()<p_rx.length():

                                p=p_lx

                            else:

                                p=p_rx

                        elif self.side=='left':

                            p=p_lx

                        elif self.side=='right':

                            p=p_rx

                        else:

                            raise ValueError("Invalid option for side :{}".format(self.side))

                    else:   # source is not tucked under the clearance

                        p0=Point(source.midpoint)

                        ll,lr,ul,ur=get_corners(bbox)

                        center_box=Point(bbox.center)

                        #left path
                        p1=Point(p0.x,destination.y+self.trace_width)

                        p2=Point(destination.x,p1.y)

                        p3=Point(destination.x,destination.y)

                        list_points=_check_points_path(p0,p1,p2,p3,trace_width=self.trace_width)

                        try:

                            p=pp.smooth(points=list_points,radius=self._radius,num_pts=self._num_pts)#source tucked inside clearance

                        except Exception:

                            raise ValueError("error for non-tucked hindered p ,90 deg")

                elif source.orientation==180 : #left path

                    p0=Point(source.midpoint)

                    p1=Point(ll.x-self.trace_width,p0.y)

                    p2=Point(p1.x,ur.y+self.trace_width)

                    p3=Point(destination.x,p2.y)

                    p4=Point(destination.x,destination.y)

                    list_points_lx=_check_points_path(p0,p1,p2,p3,p4,trace_width=self.trace_width)

                    try:

                        p=pp.smooth(points=list_points_lx,radius=self._radius,num_pts=self._num_pts)

                    except Exception:

                        import pdb; pdb.set_trace()

                        raise ValueError("error in +180 source, lx path")

        return p

    def _draw_with_frame(self):

        cell_frame=self._draw_frame()

        cell_frame.absorb(cell_frame<<self.draw())

        return cell_frame

    def _draw_non_hindered_path(self,source,destination):

        if not(destination.orientation==source.orientation+180 or \
            destination.orientation==source.orientation-180):

                raise Exception("Routing error: non-hindered routing needs +90 -> -90 oriented ports")

        distance=Point(destination.midpoint)-\
            Point(source.midpoint)

        p1=Point(source.midpoint)

        p1a=p1+Point(0,distance.y/5)
        p2=p1a+Point(distance.x,distance.y*(3/5))

        p3=p2+Point(0,distance.y/5)

        list_points=_check_points_path(p1,p1a,p2,p3,trace_width=self.trace_width)

        try:

            p=pp.smooth(points=list_points,radius=self._radius,num_pts=self._num_pts)

        except Exception:

            raise ValueError("error for non-hindered path ")

        return p

    @property
    def resistance_squares(self):

        return self.path.length()/self.trace_width

class MultiRouting(Routing):

    def __init__(self,*a,**k):

        LayoutPart.__init__(self,*a,**k)

        self.source=LayoutDefault.MultiRoutingsources
        self.destination=LayoutDefault.MultiRoutingdestinations
        self.clearance=LayoutDefault.Routingclearance
        self.trace_width=LayoutDefault.Routingtrace_width
        self.layer=LayoutDefault.Routinglayer
        self.side=LayoutDefault.Routingside

    @property
    def path(self):

        p=[]

        for s in self.source:

            for d in self.destination:

                p.append(self._make_routing(s,d))

        return p

    def _make_routing(self,s,d):

        if not all([isinstance(p, Port) for p in (s,d)]):

            raise TypeError(f"{p} is not a phidl Port")

        else:

            r=Routing()

            r.clearance=self.clearance

            r.side=self.side

            r.layer=self.layer

            r.trace_width=self.trace_width

            r.source=s

            r.destination=d

            try:

                return r.path

            except Exception as e:

                raise e

    def _draw_frame(self):

        rect=pg.bbox(self.clearance,layer=self.layer)

        for s in self.source:

            rect.add_port(s)

        for d in self.destination:

            rect.add_port(d)

        return rect

    def draw(self):

        c=Device(name=self.name)

        x=CrossSection()

        x.add(layer=self.layer,width=self.trace_width)

        for p in self.path:

            c<<x.extrude(p,simplify=0.1)

        return c

    @property
    def resistance_squares(self):

        resistance=[]

        for p in self.path:

            resistance.append(p.length()/self.trace_width)

        return resistance

class ParasiticAwareMultiRouting(MultiRouting):

    @property
    def path(self):

        numports=len(self.destination)

        if numports == 1 or numports == 2 :

            try:

                return super().path

            except Exception as e:

                raise e

        else :

            p=[]

            if numports %2 ==0:

                midport=int(numports/2)

                base_routing=deepcopy(self)

                base_routing.destination=tuple(self.destination[midport-1:midport+1])

                for dest,nextdest in zip(self.destination,self.destination[1:]):

                    if dest in base_routing.destination :

                        if nextdest in base_routing.destination:

                            p.extend(base_routing.path)

                        else:

                            p.append(self._make_paware_connection(dest,nextdest))

                    else:

                        p.append(self._make_paware_connection(dest,nextdest))

                return p

            elif numports%2==1:

                midport=int((numports-1)/2)

                base_routing=deepcopy(self)

                base_routing.destination=(self.destination[midport],)

                for dest,nextdest in zip(self.destination,self.destination[1:]):

                    if dest in base_routing.destination :

                        p.extend(base_routing.path)

                        p.append(self._make_paware_connection(dest,nextdest))

                    else:

                        p.append(self._make_paware_connection(dest,nextdest))

                return p

    def _yovertravel(self,s):
        return (s.midpoint[1]-self.source[0].midpoint[1])/4

    def _make_paware_connection(self,s,d):

        Yovertravel=self._yovertravel(s)

        p0=Point(s.midpoint)

        p1=p0-Point(0,Yovertravel)

        p2=Point(d.midpoint[0],p1.y)

        p3=Point(p2.x,d.midpoint[1])

        list_points=_check_points_path(p0,p1,p2,p3,trace_width=s.width)

        try:

            return  pp.smooth(
                        points=list_points,
                        radius=self._radius,
                        num_pts=self._num_pts)

        except Exception:

            import pdb; pdb.set_trace()

    @property
    def resistance_squares(self):

        p=self.path

        numpaths=len(p)

        pdb.set_trace()

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

                        res.append(original_res[x]-self._yovertravel(self.destination[x])/self.trace_width)

                return res

            if numpaths%2==1:

                midpoint=int((numpaths-1)/2)

                for x in range(numpaths):

                    if x==midpoint:

                        res.append(original_res[x])

                    else:

                        res.append(original_res[x]-self._yovertravel(self.destination[x])/self.trace_width)

                return res

_allclasses=(IDT,PartialEtchIDT,Bus,EtchPit,Anchor,Via,Routing,GSProbe,GSGProbe,
Pad,MultiLayerPad,ViaInPad,LFERes,FBERes,TFERes,MultiRouting,ParasiticAwareMultiRouting)

for cls in _allclasses:

    cls.draw=pirel_cache(cls.draw)

    cls() # to init _params_dict

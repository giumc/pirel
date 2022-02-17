import pirel.tools as pt

from pirel. tools import LayoutDefault as ld

import pirel.sketch_tools as st

import pirel.port_tools as ppt

from phidl.device_layout import Device, Port, DeviceReference, Group,Path

import phidl.geometry as pg

import phidl.device_layout as dl

import phidl.path as pp

import phidl.routing as pr

from pirel.tools import LayoutPart,LayoutParamInterface,LayoutDefault

from phidl import Path

from copy import copy,deepcopy

import numpy as np

class PartWithLayer(LayoutPart):
    ''' Convenience class to define a layer attribute for a LayoutPart.

    Attributes:
    -----------
        layer : int or tuple.
    '''

    layer=LayoutParamInterface(allowed_types=(int,tuple,set))

    def __init__(self,*a,**kw):

        super().__init__(*a,**kw)

        self.layer={LayoutDefault.layerTop,LayoutDefault.layerBottom}

class Text(PartWithLayer):
    ''' Class to store text data and to add it in cells.

    It controls how the text labels generated are formatted.
    You can add text to a cell using the add_text() method.

    Attributes
    -----------
    font : string
            if overridden, needs to be in pirel / path

    size : float

    label :     string
        can be multiline if '\\n' is added.
    '''

    _valid_names={'font','size','label','layer'}

    _msg_err="""Invalid key for text_param.
    Valid options are :{}""".format("\n".join(_valid_names))

    label=LayoutParamInterface()

    size=LayoutParamInterface()

    font=LayoutParamInterface()

    def __init__(self,*a,**kw):

        super().__init__(*a,**kw)

        self.layer=ld.TextLayer

        self.label=ld.TextLabel

        self.size=ld.TextSize

        self.font=ld.TextFont

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
                center=st.get_anchor(kw['anchor_source'],text_cell_ref).coord,
                angle=angle)

        except:

            text_cell_ref.rotate(
                center=st.get_anchor('ll',text_cell_ref).coord,
                angle=angle)

        st.move_relative_to_cell(text_cell_ref,cell,**kw)

        cell.add(text_cell_ref)

        return cell

    def draw(self):

        return pg.text(
            layer=self.layer,
            size=self.size,
            text=self.label,
            font=self.font)

class IDTSingle(PartWithLayer) :
    ''' Generates interdigitated structure.

        Derived from PartWithLayer.

        Attributes
        ----------
        y   :float
            finger length

        pitch : float
            finger distance

        coverage : float
            finger coverage

        n  : int
            finger number.
    '''

    length =LayoutParamInterface()

    pitch = LayoutParamInterface()

    coverage =LayoutParamInterface()

    n =LayoutParamInterface()

    active_area_margin=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.length=ld.IDT_y
        self.pitch=ld.IDTpitch
        self.coverage=ld.IDTcoverage
        self.n=ld.IDTn
        self.layer=ld.IDTlayer
        self.active_area_margin=ld.LFEResactive_area_margin

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
            spacing=(self.pitch,0))

        cell.flatten()

        r=st.get_corners(cell)

        port_width=cell.xsize+(1-self.coverage)*self.pitch

        cell.add_port(
            Port(name='bottom',
            midpoint=r.s.coord,
            width=port_width,
            orientation=-90))

        cell.add_port(
            Port(name='top',
            midpoint=r.n.coord,
            width=port_width,
            orientation=90))

        del unitcell

        return cell

    def get_finger_size(self):
        ''' get finger length and width.

        Returns
        -------
        size : PyResLayout.pt.Point
            finger size as coordinates lenght(length) and width(x).
        '''
        dy=self.length

        dx=self.pitch*self.coverage

        return pt.Point(dx,dy)

    @property
    def active_area(self):

        x=self.pitch*self.n+2*self.active_area_margin

        y=self.length

        return pt.Point(x,y)

    @property
    def probe_distance(self):

        return pt.Point(0,self.active_area.x)

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

        rect=pg.rectangle(
            size=(self.coverage*self.pitch,self.length),
            layer=self.layer)

        rect.name="UnitCell"

        return rect

class IDT(PartWithLayer) :
    ''' Generates interdigitated structure.

        Derived from PartWithLayer.

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

        n  : int
            finger number.
    '''

    length =LayoutParamInterface()

    pitch = LayoutParamInterface()

    y_offset =LayoutParamInterface()

    coverage =LayoutParamInterface()

    n =LayoutParamInterface()

    active_area_margin=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.length=ld.IDT_y
        self.pitch=ld.IDTpitch
        self.y_offset=ld.IDTy_offset
        self.coverage=ld.IDTcoverage
        self.n=ld.IDTn
        self.layer=ld.IDTlayer
        self.active_area_margin=ld.LFEResactive_area_margin

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

        finger_dist=pt.Point(self.pitch*1,\
        self.length+self.y_offset)

        cell=st.join(cell)

        cell.name=self.name

        cell.add_port(
            Port(name='bottom',
            midpoint=(
                pt.Point(midx,0).coord),
            width=totx,
            orientation=-90))

        cell.add_port(
            name='top',
            midpoint=pt.Point(midx,self.length+self.y_offset).coord,
            width=totx,
            orientation=90)

        del unitcell

        return cell

    def get_finger_size(self):
        ''' get finger length and width.

        Returns
        -------
        size : PyResLayout.pt.Point
            finger size as coordinates lenght(length) and width(x).
        '''
        dy=self.length

        dx=self.pitch*self.coverage

        return pt.Point(dx,dy)

    @property
    def active_area(self):

        x=self.pitch*(self.n*2+1)+2*self.active_area_margin

        y=self.length+self.y_offset

        return pt.Point(x,y)

    @property
    def probe_distance(self):

        return pt.Point(0,self.active_area.x*0.7)

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

        rect=pg.rectangle(
            size=(self.coverage*self.pitch,self.length),
            layer=self.layer)

        unitcell=Device()

        r1=unitcell << rect

        unitcell.absorb(r1)

        r2 = unitcell << rect

        r2.move(
            destination=pt.Point(self.pitch,self.y_offset).coord)

        r3= unitcell<< rect

        r3.move(
            destination=pt.Point(2*self.pitch,0).coord)

        unitcell.absorb(r2)

        unitcell.absorb(r3)

        unitcell.name="UnitCell"

        del rect

        return unitcell

class PartialEtchIDT(IDT):

    layer_partialetch=LayoutParamInterface()

    def __init__(self,*a,**kw):

        super().__init__(*a,**kw)

        self.layer_partialetch=ld.layerPartialEtch

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
            destination=pt.Point(self.pitch,self.y_offset).coord)

        r3= unitcell<< rect

        r3.move(
            destination=pt.Point(2*self.pitch,0).coord)

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

class Bus(PartWithLayer) :
    ''' Generates pair of bus structure.

    Attributes
    ----------
    size : PyResLayout.pt.Point
        bus size coordinates of length(y) and width(x)
    distance : PyResLayout.pt.Point
        distance between buses coordinates.
    '''
    size=LayoutParamInterface()

    distance=LayoutParamInterface()



    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer = ld.layerTop

        self.size=copy(ld.Bussize)

        self.distance=copy(ld.Busdistance)

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
        midpoint=pt.Point(self.size.x/2,self.size.y).coord,
        width=self.size.x,
        orientation=90)

        return cell

    @property
    def resistance_squares(self):

        return self.size.x/self.size.y/2

class EtchPit(PartWithLayer) :
    ''' Generates pair of etching trenches.

    Attributes
    ----------
    active_area : PyResLayout.pt.Point
        area to be etched as length(Y) and width(X)
    x : float
        etch width.
    '''

    active_area=LayoutParamInterface()

    x=LayoutParamInterface()



    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.active_area=copy(ld.EtchPitactive_area)

        self.x=ld.EtchPit_x

        self.layer=ld.EtchPitlayer

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
        midpoint=pt.Point(self.x+self.active_area.x/2,self.active_area.y).coord,
        width=self.active_area.x,
        orientation=-90)

        port_down=Port('bottom',
        midpoint=pt.Point(self.x+self.active_area.x/2,0).coord,
        width=self.active_area.x,
        orientation=90)

        etch.add_port(port_up)
        etch.add_port(port_down)

        return etch

class Anchor(PartWithLayer):
    ''' Generates anchor structure.

    Attributes
    ----------
    size :
        length(Y) and size(X) of anchors

    metalized : PyResLayout.pt.Point
        metal connection

    etch_choice: boolean
        to add or not etching patterns

    etch_x : float
        width of etch pit

    etch_layer : int
        etch layer.

    '''

    size=LayoutParamInterface()
    metalized=LayoutParamInterface()
    etch_choice=LayoutParamInterface(allowed_values={False,True})
    etch_x=LayoutParamInterface()
    x_offset=LayoutParamInterface()

    etch_layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.size=ld.Anchorsize
        self.metalized=ld.Anchor_metalized
        self.etch_choice=ld.Anchoretch_choice
        self.etch_x=ld.Anchoretch_x
        self.x_offset=ld.Anchorx_offset
        self.layer=ld.Anchorlayer
        self.etch_layer=ld.Anchoretch_layer

    def draw(self):

        self._check_anchor()

        anchor=self._draw_metalized()

        etch_size=pt.Point(
        (self.etch_x-self.size.x)/2,
        self.size.y)

        offset=pt.Point(self.x_offset,0)

        cell=Device(self.name)

        etch_sx=pg.rectangle(
            size=(etch_size-offset).coord,
            layer=self.etch_layer)

        etch_dx=pg.rectangle(
            size=(etch_size+offset).coord,
            layer=self.etch_layer)

        etch_sx_ref=(cell<<etch_sx).move(
        destination=(pt.Point(0,self.etch_margin.y)).coord)

        # anchor_transl=pt.Point(etch_sx.size[0]+self.etch_margin.x,-2*self.etch_margin.y)

        anchor_transl=pt.Point(etch_sx.xsize+self.etch_margin.x,0)

        anchor_ref=(cell<<anchor).move(
            destination=anchor_transl.coord)

        etchdx_transl=anchor_transl+pt.Point(anchor.xsize+self.etch_margin.x,self.etch_margin.y)

        etch_dx_ref=(cell<<etch_dx).move(
            destination=etchdx_transl.coord)

        ppt.copy_ports(anchor_ref,cell)

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
            size=(self.size-pt.Point(2*self.etch_margin.x,-2*self.etch_margin.y)).coord,
            layer=self.layer)

        r=st.get_corners(cell)

        cell.add_port(name='top',midpoint=r.n.coord,width=cell.xsize,orientation=90)

        cell.add_port(name='bottom',midpoint=r.s.coord,width=cell.xsize,orientation=270)

        return cell

    @property
    def resistance_squares(self):

        return 2*self.metalized.y/self.metalized.x

    @property
    def etch_margin(self):

        return pt.Point(
            (self.size.x-self.metalized.x)/2,
            (self.metalized.y-self.size.y)/2)

    def _check_anchor(self):

        if self.metalized.x>=self.size.x:

            # warnings.warn(f"""Metalized X capped to {self.size.x*0.9 :.2f}\n""")
            self.metalized=pt.Point(self.size.x*0.9,self.metalized.y)

        if self.metalized.y<=self.size.y:

            # warnings.warn(f"""Metalized Y capped to {self.size.y*1.1 : .2f}""")
            self.metalized=pt.Point(self.metalized.x,self.size.y*1.1)

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

        self.n=ld.MultiAnchorn

        self.spacing=pt.Point(self.size.x/3,0)

    def _draw_metalized(self):

        if self.n>1:

            self._check_anchor()

            metalized=super()._draw_metalized()

            metalized_all=pt.draw_array(
                metalized,x=self.n,y=1,
                row_spacing=self.spacing.y,column_spacing=self.spacing.x+self.etch_margin.x*2)

            inner_etch=pg.rectangle(
                size=(self.spacing.x,self.size.y),
                layer=self.etch_layer)

            for i in range(0,self.n-1):

                ref=metalized_all<<inner_etch

                anchor_dest=pt.Point(metalized_all.ports['top'+"_"+str(i)].endpoints[1])

                ref.move(
                    origin=(ref.xmin,ref.ymax),
                    destination=(anchor_dest+pt.Point(self.etch_margin.x,-self.etch_margin.y)).coord)

                metalized_all.absorb(ref)

            return metalized_all

        else:

            return super()._draw_metalized()

    def draw(self):

        cell=Device(self.name)

        anchor_metal=cell<<self._draw_metalized()

        remaining_x_lx=(self.etch_x-self.active_x)/2-self.x_offset

        lx_etch=cell<<pg.rectangle(
            size=(remaining_x_lx,self.size.y),
            layer=self.etch_layer)

        remaining_x_rx=(self.etch_x-self.active_x)/2+self.x_offset

        rx_etch=cell<<pg.rectangle(
            size=(remaining_x_rx,self.size.y),
            layer=self.etch_layer)

        g=Group(lx_etch,anchor_metal,rx_etch)

        g.align(alignment='x')

        g.align(alignment='y')

        g.distribute(spacing=self.etch_margin.x)

        ppt.copy_ports(anchor_metal,cell)

        if not self.etch_choice:

            cell.remove(rx_etch)

            cell.remove(lx_etch)

        if self.n>1:

            if self.n%2==1:

                p=cell.ports['top'+'_'+str(int((self.n-1)/2))]

                cell.add_port(port=p,name='top')

            else:
                cell.add_port(
                    Port(
                        name='top',
                        midpoint=(cell.x,cell.ymax),
                        width=cell.ports['top_0'].width,
                        orientation=90
                        )
                    )

        return cell

    @property
    def active_x(self):

        return self.spacing.x*(self.n-1)+self.n*self.size.x

    def _check_anchor(self):

        super()._check_anchor()

        if self.active_x>=self.etch_x:

            raise ValueError(f"{self.__class__.__name__} error: anchor(s) size needs {self.active_x}, while etch area is only {self.etch_x}")

class Via(PartWithLayer):
    ''' Generates via pattern.

    Attributes
    ----------
    size : float
        if shape is 'square', side of square
        if shape is 'circle', diameter of cirlce

    shape : str (only 'square' or 'circle')
        via shape.
    '''

    size=LayoutParamInterface()

    shape=LayoutParamInterface(allowed_values={'square','circle'})

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=ld.Vialayer
        self.shape=ld.Viashape
        self.size=ld.Viasize
        self.conn_layer=(ld.layerTop,ld.layerBottom)

    def draw(self):

        if self.shape=='square':

            cell=pg.rectangle(size=(self.size,self.size),
                layer=self.layer)

        elif self.shape=='circle':

            cell=pg.circle(radius=self.size/2,\
            layer=self.layer)

        else:

            raise ValueError("Via shape can be \'square\' or \'circle\'")

        cell.add_port(Port(name='conn',\
        midpoint=cell.center,\
        width=cell.xmax-cell.xmin,\
        orientation=90))

        return cell

class Probe(LayoutPart):
    '''
    Attributes
    ----------
    size : PyResLayout.pt.Point

    pitch : float
        probe pitch

    sig_layer : tuple of int
        signal layer

    ground_layer : tuple of int
        ground layer.
    '''

    pitch=LayoutParamInterface()

    size=LayoutParamInterface()

    sig_layer=LayoutParamInterface()

    ground_layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.sig_layer=ld.Probesiglayer
        self.ground_layer=ld.Probegroundlayer
        self.pitch=ld.Probepitch
        self.size=ld.Probesize

class GSProbe(Probe):
    ''' Generates GS pattern.'''

    def draw(self):

        name=self.name

        pad_x=self.size.x

        if pad_x>self.pitch*2/3:

            pad_x=self.pitch*2/3

            # warnings.warn("Pad size too large, capped to pitch*2/3")

        pad_cell=pg.rectangle(
            layer=self.sig_layer,
            size=(pad_x,self.size.y))

        cell=Device(self.name)

        dp=pt.Point(self.pitch,0)

        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell

        cell.add_port(Port(name='gnd_left',
        midpoint=pt.Point(pad_x/2+self.pitch,self.size.y).coord,
        width=pad_x,
        orientation=90))

        cell.add_port(Port(name='sig',
        midpoint=pt.Point(pad_x/2,self.size.y).coord,
        width=pad_x,
        orientation=90))

        return cell

class GSGProbe(Probe):
    ''' Generates GSG pattern.'''

    def draw(self):

        name=self.name

        pad_x=self.size.x

        if pad_x>self.pitch*9/10:

            pad_x=self.pitch*9/10

            # warnings.warn("Pad size too large, capped to pitch*9/10")

        sig_cell=pg.compass(
            layer=self.sig_layer,
            size=(pad_x,self.size.y))

        gnd_cell=pg.compass(
            layer=self.ground_layer,
            size=(pad_x,self.size.y))

        cell=Device(self.name)

        dp=pt.Point(self.pitch,0)

        pad_gnd_lx=cell.add_ref(gnd_cell,alias='GroundLX')

        pad_sig=cell.add_ref(sig_cell,alias='Sig')
        pad_sig.move(destination=dp.coord)

        pad_gnd_rx=cell.add_ref(gnd_cell,alias='GroundRX')
        pad_gnd_rx.move(destination=(2*dp).coord)

        ppt.copy_ports(pad_sig,cell,prefix='Sig')
        ppt.copy_ports(pad_gnd_rx,cell,prefix='GroundRX')
        ppt.copy_ports(pad_gnd_lx,cell,prefix='GroundLX')

        return cell

class Pad(PartWithLayer):
    ''' Generates Pad geometry.


    Attributes
    ----------
    size : float
        pad square side

    distance : float
        distance between pad edge and port

    port : phidl.Port
        port to connect pad to.
    '''

    size=LayoutParamInterface()

    distance=LayoutParamInterface()

    port=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.size=ld.Padsize
        self.layer=ld.Padlayer
        self.distance=copy(ld.Paddistance)
        self.port=ld.Padport

    def draw(self):

        r1=pg.compass(
            layer=self.layer,
            size=(self.port.width,self.distance))

        north_port=r1.ports['N']
        south_port=r1.ports['S']

        r2=pg.compass(
            layer=self.layer,
            size=(self.size,self.size))

        sq_ref=r1<<r2

        sq_ref.connect(r2.ports['S'],
            destination=north_port)

        r1.absorb(sq_ref)

        r1=st.join(r1)

        r1.add_port(port=south_port,name='conn')

        return r1

    @property
    def resistance_squares(self):

        return 1+self.distance/self.port.width

class ViaInPad(Pad):

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

        bus_ref.connect(
            port=bus_cell.ports['conn'],
            destination=idt_bottom_port)

        etch_cell=self.etchpit.draw()

        etch_ref=cell.add_ref(etch_cell,alias='EtchPit')

        etch_ref.connect(
            etch_ref.ports['bottom'],
            destination=idt_ref.ports['bottom'],
            overlap=-self.bus.size.y-self.anchor.etch_margin.y)

        anchor_cell=self.anchor.draw()

        anchor_bottom=cell.add_ref(anchor_cell,alias='AnchorBottom')

        anchor_bottom.connect(
            anchor_bottom.ports['top'],
            destination=idt_ref.ports['bottom'],overlap=-self.bus.size.y)

        if not self._stretch_top_margin:

            anchor_top=cell.add_ref(anchor_cell,alias='AnchorTop')

        else:

            anchor_top_dev=deepcopy(self.anchor)

            anchor_top_dev.metalized=pt.Point(anchor_top_dev.size.x-2,anchor_top_dev.metalized.y)

            anchor_top=cell.add_ref(anchor_top_dev.draw(),alias='AnchorTop')

        anchor_top.connect(anchor_top.ports['top'],
            idt_ref.ports['top'],overlap=-self.bus.size.y)

        if self.anchor.n>1:

            for i,p in enumerate(ppt.find_ports(anchor_top,'bottom')):
                #port name switched because top anchor is flipped
                port_num_flipped=int(p.name[-1])

                cell.add_port(port=p,name='top'+'_'+str(self.anchor.n-1-port_num_flipped))

            for p in ppt.find_ports(anchor_bottom,'bottom'):

                cell.add_port(p)

        else:

            cell.add_port(port=anchor_top.ports['bottom'],name='top')

            cell.add_port(anchor_bottom.ports['bottom'])

        return cell

    def get_params(self):

        LFERes._set_relations(self)

        t=super().get_params()

        pt.pop_all_dict(t,["IDT"+x for x in ["Name"]])

        pt.pop_all_dict(t, ["Bus"+x for x in ['Name','DistanceX','DistanceY','SizeX']])

        pt.pop_all_dict(t,["EtchPit"+x for x in['Name','ActiveAreaX','ActiveAreaY']])

        pt.pop_all_dict(t,["Anchor"+x for x in ['Name','EtchX','XOffset','EtchChoice']])

        return t

    def _set_params(self,df):

        super()._set_params(df)

        LFERes._set_relations(self)

    def _set_relations(self):

        self.bus.size=pt.Point(
            self.idt.active_area.x-\
            2*self.idt.active_area_margin-\
            self.idt.pitch*(1-self.idt.coverage),\
            self.bus.size.y)

        self.bus.distance=pt.Point(\
            0,self.idt.active_area.y+self.bus.size.y)

        self.bus.layer=self.idt.layer

        self.etchpit.active_area=pt.Point(self.idt.active_area.x,
            self.idt.active_area.y+2*self.bus.size.y+self.anchor.etch_margin.y*2)

        self.anchor.etch_x=self.etchpit.x*2+self.etchpit.active_area.x

        self.anchor.layer=self.idt.layer

        # if self.anchor.metalized.x>self.bus.size.x:
        #
        #     warnings.warn(f"Anchor metalized X reduced to {self.bus.size.x}")
        #
        #     self.anchor.metalized=pt.Point(\
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

    @property
    def active_area(self):

        return pt.Point(
            self.idt.active_area.x+2*self.etchpit.x,
            self.idt.active_area.y+2*self.bus.size.y+2*self.anchor.metalized.y)

    @staticmethod
    def get_components():

        return {'IDT':IDT,"Bus":Bus,"EtchPit":EtchPit,"Anchor":MultiAnchor}

class TwoDMR(LayoutPart):

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

        bus_ref=cell.add_ref(pg.rectangle(
            size=(self.bus.size.x,self.bus.size.y),
            layer=self.bus.layer),alias='Bus')

        bus_ref.move(
            origin=(bus_ref.x,bus_ref.ymin),
            destination=(idt_ref.x,idt_ref.ymax))

        etch_cell=self.etchpit.draw()

        etch_ref=cell.add_ref(etch_cell,alias='EtchPit')

        etch_ref.connect(
            etch_ref.ports['bottom'],
            destination=idt_ref.ports['bottom'],
            overlap=-self.bus.size.y-self.anchor.etch_margin.y)

        anchor_cell=self.anchor.draw()

        anchor_top=cell.add_ref(anchor_cell,alias='AnchorTop')

        anchor_cell_bottom=st.join(anchor_cell).remove_polygons(lambda pt,lay,dt : lay==self.anchor.layer )

        ppt.copy_ports(anchor_top,anchor_cell_bottom)

        anchor_bottom=cell.add_ref(anchor_cell_bottom,alias='AnchorBottom')

        anchor_top.connect(anchor_top.ports['top'],
            idt_ref.ports['top'],overlap=-self.bus.size.y)

        anchor_bottom.connect(anchor_bottom.ports['top'],
            idt_ref.ports['bottom'],overlap=-self.bus.size.y)

        if self.anchor.n>1:

            for i,p in enumerate(ppt.find_ports(anchor_top,'bottom')):
                #port name switched because top anchor is flipped
                port_num_flipped=int(p.name[-1])

                cell.add_port(port=p,name='top'+'_'+str(self.anchor.n-1-port_num_flipped))

        else:

            cell.add_port(port=anchor_top.ports['bottom'],name='top')
            cell.add_port(anchor_bottom.ports['bottom'])

        return cell

    def get_params(self):

        LFERes._set_relations(self)

        t=super().get_params()

        pt.pop_all_dict(t,["IDT"+x for x in ["Name"]])

        pt.pop_all_dict(t, ["Bus"+x for x in ['Name','DistanceX','DistanceY','SizeX']])

        pt.pop_all_dict(t,["EtchPit"+x for x in['Name','ActiveAreaX','ActiveAreaY']])

        pt.pop_all_dict(t,["Anchor"+x for x in ['Name','EtchX','XOffset','EtchChoice']])

        return t

    def _set_params(self,df):

        super()._set_params(df)

        LFERes._set_relations(self)

    def _set_relations(self):

        self.bus.size=pt.Point(
            self.idt.active_area.x-
            2*self.idt.active_area_margin-
            self.idt.pitch*(1-self.idt.coverage),
            self.bus.size.y)

        self.bus.distance=pt.Point(0,self.idt.active_area.y+self.bus.size.y)

        self.bus.layer=self.idt.layer

        self.etchpit.active_area=pt.Point(
            self.idt.active_area.x,
            self.idt.active_area.y+2*self.bus.size.y+self.anchor.etch_margin.y*2)

        self.anchor.etch_x=self.etchpit.x*2+self.etchpit.active_area.x

        self.anchor.layer=self.idt.layer

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

        return {'IDT':IDTSingle,"Bus":Bus,"EtchPit":EtchPit,"Anchor":MultiAnchor}

def addBottomPlate(cls):

    class BottomPlated(cls):

        plate_under_bus=LayoutParamInterface(allowed_values={True,False})

        plate_over_etch=LayoutParamInterface(allowed_values={True,False})

        plate_layer=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.plate_under_bus=True

            self.plate_over_etch=False

            self.plate_layer=ld.FBEResplatelayer

        def draw(self):

            cell=Device()

            cell.name=self.name

            supercell=cls.draw(self)

            super_ref=cell.add_ref(supercell,alias=cls.__name__)

            super_r=st.get_corners(supercell)

            if self.plate_over_etch:

                size_x=self.etchpit.active_area.x+8*self.idt.active_area_margin

            else:

                size_x=self.etchpit.active_area.x-2*self.idt.active_area_margin

            if self.plate_under_bus:

                size_y=self.idt.length+2*self.bus.size.y+self.idt.y_offset

            else:

                size_y=self.idt.length-self.idt.y_offset

            plate=pg.rectangle(
                size=(size_x,size_y),
                layer=self.plate_layer)

            plate_ref=cell.add_ref(plate,alias='Plate')

            r=st.get_corners(plate_ref)

            if self.plate_under_bus:

                trasl=pt.Point(0,-self.anchor.metalized.y)

            else:

                trasl=pt.Point(0,-self.anchor.metalized.y-self.bus.size.y-self.idt.y_offset)

            plate_ref.move(
                origin=r.n.coord,
                destination=(super_r.n+trasl).coord)

            cell.absorb(plate_ref)

            ppt.copy_ports(supercell,cell)

            return cell

    BottomPlated.__name__=" ".join(["BottomPlated",cls.__name__])

    return BottomPlated

FBERes=addBottomPlate(LFERes)

class TwoPortRes(FBERes):

    def __init__(self,*a,**k):

        super().__init__(*a,**k)

        self.plate_under_bus=True

        self.plate_over_etch=False

        self.plate_layer=ld.layerBottom

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

        ppt.copy_ports(supercell,cell)

        self._make_ground_connections(cell)

        return cell

    def _bbox_mod(self,bbox):

        ll=pt.Point(bbox[0])

        ur=pt.Point(bbox[1])

        return ((ll.x+self.anchor.metalized.x+0.005,ll.y),
                (ur.x-self.anchor.metalized.x-0.005,ur.y))

    def _make_ground_connections(self,cell):

        r=st.get_corners(cell)

        margin=pt.Point(self.anchor.size.x-self.anchor.metalized.x,0)

        cell.add_port(
            name='GroundLX',
            midpoint=(r.w-margin).coord,
            width=r.ul.y-r.ll.y,
            orientation=180)

        cell.add_port(
            name='GroundRX',
            midpoint=(r.e+margin).coord,
            width=r.ur.y-r.lr.y,
            orientation=0)

        ground_port_lx=cell.ports["GroundLX"]
        ground_port_rx=cell.ports["GroundRX"]

        for corner,sig,tag in zip([r.ll,r.lr,r.ul,r.ur],[-1,1,-1,1],['bottom','bottom','top','top']):

            cell_ports=ppt.find_ports(cell,tag,depth=0)

            conn_width=cell_ports[0].width

            if tag=='top':

                orient=90

            elif tag=='bottom':
                orient=270

            conn_port=Port(
                width=conn_width,
                midpoint=(corner+sig*pt.Point(conn_width/2,0)+sig*margin).coord,
                orientation=orient)

            rou=MultiRouting()
            rou.layer=(self.plate_layer,)
            rou.source=tuple(cell_ports)
            rou.destination=(conn_port,)
            rou.overhang=conn_width
            rou.trace_width=None
            cell.add(rou.draw())

class TFERes(LFERes):

    bottom_layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.bottom_layer=ld.layerBottom

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

        bus_ref.move(
            destination=(0,-self.bus.size.y))

        anchor_bottom=deepcopy(self.anchor)

        anchor_bottom.layer=self.bottom_layer

        anchor_bottom.etch_choice=False

        anchor_ref=cell.add_ref(anchor_bottom.draw(),alias="BottomAnchor_Top")

        anchor_ref.connect(anchor_ref.ports['top'],
            destination=idt_ref.ports['top'],overlap=-self.bus.size.y-self.idt.y_offset)

        # anchor_ref.rotate(center=anchor_ref.ports['top'].midpoint,angle=180)

        anchor_ref_2=cell.add_ref(anchor_bottom.draw(),alias="BottomAnchor_Top")

        anchor_ref_2.connect(anchor_ref_2.ports['top'],
            destination=idt_ref.ports['bottom'],overlap=-self.bus.size.y-self.idt.y_offset)

        # anchor_ref_2.rotate(center=anchor_ref_2.ports['top'].midpoint,angle=180)

        ppt.copy_ports(lfe_cell,cell)

        return cell

class SMD(PartWithLayer):
    ''' Generate pad landing for SMD one-port component

    Attributes
    ----------
    size : pt.Point

    distance :pt.Point.
    '''



    size=LayoutParamInterface()

    distance=LayoutParamInterface()

    def __init__(self,*a,**kw):

        super().__init__(*a,**kw)
        self.layer=ld.SMDLayer
        self.distance=ld.SMDDistance
        self.size=ld.SMDSize

    def draw(self):

        unit_pad=Device()

        unit_pad.add_ref(
            pg.compass(
                size=self.size.coord,
                layer=self.layer),
            alias='layer'+str(l))

        cell=Device(name=self.name)

        ppt.copy_ports(pg.compass(size=self.size.coord,layer=l),unit_pad)

        p1=cell.add_ref(unit_pad,alias='Pad_1')
        p2=cell.add_ref(unit_pad,alias='Pad_2')

        p2.move(destination=self.distance.coord)

        ppt.copy_ports(p1,cell,suffix='_1')
        ppt.copy_ports(p2,cell,suffix='_2')

        return cell

    def set_01005(self):

        self.size=pt.Point(300,250)

        self.distance=pt.Point(0,400)

class Routing(PartWithLayer):
    ''' Generate automatic routing connection

    Attributes
    ----------
    clearance : iterable of two coordinates
        bbox of the obstacle

    source: phidl.Port (or iterable of phidl.Port)

    overhang: float
        distance to extend port in its direction before routing
        if None, overhang is set automatically

    destination: phidl.Port (or iterable of phidl.Port)

    side : str (can be "auto","left","right")
        where to go if there is an obstacle.
        decides where to go if there is an obstacle in the routing,
        only 'auto','left','right'.
    '''

    _num_pts=np.arange(50,1000,20)

    clearance=LayoutParamInterface()

    overhang=LayoutParamInterface()

    type=LayoutParamInterface(
        allowed_values={'manhattan','L','U','J','C','V','Z','straight'})

    source=LayoutParamInterface()

    destination=LayoutParamInterface()

    trace_width=LayoutParamInterface()

    side=LayoutParamInterface(allowed_values={'auto','left','right'})

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.clearance=ld.Routingclearance
        self.type=ld.Routingtype
        self.source=ld.Routingports[0]
        self.destination=ld.Routingports[1]
        self.layer=ld.Routinglayer
        self.overhang=ld.Routingoverhang
        self.trace_width=ld.Routingtrace_width
        self.side=ld.Routingside
        self._auto_overhang=False

    def _check_frame(self):

        cell=self._draw_frame()

        st.check(cell)

    def _draw_frame(self):

        frame=pg.bbox(self.clearance,layer=self.layer)

        for s in pt._return_iterable(self.source):

            frame.add_port(s)

        for d in pt._return_iterable(self.destination):

            frame.add_port(d)

        return frame

    def draw(self):

        cell=Device(self.name)

        for s in pt._return_iterable(self.source):

            for d in pt._return_iterable(self.destination):

                cell.add(self._draw_path_cell(self._make_path(s,d),s,d))

        return st.join(cell)

    def _make_path(self,s,d):

        self._check_if_ports_in_clearance(s,d)

        try:

            p=self._draw_non_hindered_path(s,d)

        except ValueError as e_non_hind:

            p=self._draw_hindered_path(s,d,self.side)

        return p

    def _check_if_ports_in_clearance(self,s,d):

        if pt.Point(s.midpoint).in_box(self.clearance) :

            raise ValueError(f" Source of routing {s.midpoint} is in clearance area {self.clearance}")

        if pt.Point(d.midpoint).in_box(self.clearance):

            # pt.Point(d.midpoint).in_box(self.clearance)
            raise ValueError(f" Destination of routing {d.midpoint} is in clearance area{self.clearance}")

    def _draw_with_frame(self):

        cell_frame=self._draw_frame()

        cell_frame.absorb(cell_frame<<self.draw())

        return cell_frame

    def _draw_non_hindered_path(self,s,d):

        p1,p1_proj,p2_proj,p2=self._calculate_start_end_connection_points(s,d)

        for p_mid in (pt.Point(p1_proj.x,p2_proj.y),pt.Point(p2_proj.x,p1_proj.y)):

            points=[p1,p1_proj,p_mid,p2_proj,p2]

            pt._remove_duplicates(points)

            pt._remove_backward_points(points)

            p=Path(tuple([x.coord for x in points]))

            if not self._is_hindered(p,s,d):

                break

        else:

            raise ValueError("path is hindered")

        return p

    def _draw_hindered_path(self,s,d,side='auto'):

        r=st.get_corners(pg.bbox(self.clearance))

        extra_width=self._get_max_width()

        if side=='auto':

            path1=self._draw_hindered_path(s,d,'left')

            path2=self._draw_hindered_path(s,d,'right')

            if path2.length()<path1.length() : return path2

            else : return path1

        p1,p1_proj,p2_proj,p2=self._calculate_start_end_connection_points(s,d)

        if side=='left':

            p_below_clearance=pt.Point(r.ll.x-extra_width,p1_proj.y)

        elif side=='right':

            p_below_clearance=pt.Point(r.lr.x+extra_width,p1_proj.y)

        p_above_clearance=pt.Point(p_below_clearance.x,r.ur.y+(r.ll.y-p1_proj.y))

        p_at_dest=pt.Point(p_below_clearance.x,p2_proj.y)

        if abs(p_at_dest-p_below_clearance)<=abs(p_above_clearance-p_below_clearance):

            p_mid2=p_at_dest

        else:

            p_mid2=p_above_clearance

        for p_mid3 in (pt.Point(p_mid2.x,p2_proj.y),pt.Point(p2_proj.x,p_mid2.y)):

            points=[p1,p1_proj,p_below_clearance,p_mid2,p_mid3,p2_proj,p2]

            pt._remove_duplicates(points)

            pt._remove_backward_points(points)

            p=Path(tuple([x.coord for x in points]))

        #     if not self._is_hindered(p,s,d):
        #
        #         break
        #
        # else:
        #
        #     raise ValueError("path is impossible")

        return p

    def _is_hindered(self,p,s,d):

        test_path_cell=self._draw_path_cell(p,s,d)

        if self.clearance==((0,0),(0,0)):

            return False

        else:

            return not st.is_cell_outside(
                pg.union(test_path_cell),
                pg.bbox(self.clearance,layer=self.layer),
                tolerance=0)

    def _draw_path_cell(self,p,s,d):

        if self.trace_width is None:

            return p.extrude(
                layer=self.layer,
                width=[s.width,d.width])

        else:

            return p.extrude(
                layer=self.layer,
                width=self.trace_width)

    def _calculate_start_end_connection_points(self,s,d):

        p1=pt.Point(s.midpoint)

        p2=pt.Point(d.midpoint)

        if self.overhang is None:

            overhang=self._calculate_overhang(s,d)

        else:

            overhang=self.overhang

        dt1_norm=pt.Point(s.normal[1])-pt.Point(s.normal[0])

        p1_proj=p1+dt1_norm*overhang

        dt2_norm=pt.Point(d.normal[1])-pt.Point(d.normal[0])

        p2_proj=p2+dt2_norm*overhang

        return p1,p1_proj,p2_proj,p2

    @staticmethod
    def _calculate_overhang(s,d):

        p1=pt.Point(s.midpoint)
        p2=pt.Point(d.midpoint)

        dist=abs(p2-p1)

        return dist/5

    @property
    def resistance_squares(self):

        return self.path.length()/self._get_max_width()

    def _get_max_width(self):

        width=0

        for s in pt._return_iterable(self.source):

            for d  in pt._return_iterable(self.destination):

                if s.width>width :

                    width=s.width

                if d.width>width:

                    width=d.width

        return width
#
# class ParasiticAwareMultiRouting(MultiRouting):
#
#     @property
#     def path(self):
#
#         numports=len(self.destination)
#
#         if numports == 1 or numports == 2 :
#
#             return super().path
#
#         else :
#
#             p=[]
#
#             if numports %2 == 0:
#
#                 midport=int(numports/2)
#
#                 base_routing=deepcopy(self)
#
#                 base_routing.destination=tuple(self.destination[midport-1:midport+1])
#
#                 for dest,nextdest in zip(self.destination,self.destination[1:]):
#
#                     if dest in base_routing.destination :
#
#                         if nextdest in base_routing.destination:
#
#                             p.extend(base_routing.path)
#
#                         else:
#
#                             p.append(self._draw_non_hindered_path(dest,nextdest))
#
#                     else:
#
#                         p.append(self._draw_non_hindered_path(dest,nextdest))
#
#                 return p
#
#             elif numports %2 == 1:
#
#                 midport=int((numports-1)/2)
#
#                 base_routing=deepcopy(self)
#
#                 base_routing.destination=(self.destination[midport],)
#
#                 for dest,nextdest in zip(self.destination,self.destination[1:]):
#
#                     if dest in base_routing.destination :
#
#                         p.extend(base_routing.path)
#
#                         p.append(self._draw_non_hindered_path(dest,nextdest))
#
#                     else:
#
#                         p.append(self._draw_non_hindered_path(dest,nextdest))
#
#                 return p
#
#     def _make_paware_connection(self,s,d):
#
#         p1=pt.Point(s.midpoint)
#
#         p2=pt.Point(d.midpoint)
#
#         p1=p0+pt.Point(0,self.overhang)
#
#         p2=pt.Point(d.midpoint[0],p1.y)
#
#         p3=pt.Point(p2.x,d.midpoint[1])
#
#         return self._make_path(p0,p1,p2,p3)
#
#     @property
#     def resistance_squares(self):
#
#         p=self.path
#
#         numpaths=len(p)
#
#         if numpaths==1 or numpaths==2:
#
#             return super().resistance_squares
#
#         else:
#
#             original_res=super().resistance_squares
#
#             res=[]
#
#             if numpaths%2==0:
#
#                 midpoint=int(numpaths/2)
#
#                 for x in range(numpaths):
#
#                     if x==midpoint-1 or x==midpoint:
#
#                         res.append(original_res[x])
#
#                     else:
#
#                         res.append(original_res[x]-self._yovertravel(self.destination[x])/self._get_max_width()[x])
#
#                 return res
#
#             if numpaths%2==1:
#
#                 midpoint=int((numpaths-1)/2)
#
#                 for x in range(numpaths):
#
#                     if x==midpoint:
#
#                         res.append(original_res[x])
#
#                     else:
#
#                         res.append(original_res[x]-self._yovertravel(self.destination[x])/self.trace_width)
#
#                 return res

_allclasses=(Text,IDTSingle,IDT,PartialEtchIDT,Bus,EtchPit,Anchor,MultiAnchor,Via,Routing,GSProbe,GSGProbe,
Pad,ViaInPad,LFERes,TwoDMR,TwoPortRes,TFERes)

for cls in _allclasses:

    cls.draw=pt._pirel_cache(cls.draw)

    cls() # to init _params_dict

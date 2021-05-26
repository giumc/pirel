from pirel.tools import *

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

        text_cell=Device(name=self.get('label')+"Text").add(self.draw()).flatten()

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

        package_directory = str(pathlib.path(__file__).parent/'addOns')

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

class PEtchIDT(IDT):

    def _draw_unit_cell(self):

        o=self.origin

        rect=pg.rectangle(size=(self.coverage*self.pitch,self.length),\
            layer=self.layer)

        rect.move(origin=(0,0),destination=o.coord)

        unitcell=Device()

        r1=unitcell << rect

        unitcell.absorb(r1)

        rect_partialetch=pg.rectangle(\
            size=(\
                (1-self.coverage)*self.pitch,self.length-self.y_offset),\
            layer=LayoutDefault.layerPartialEtch)

        rect_partialetch.move(origin=o.coord,\
            destination=(self.pitch*self.coverage,self.y_offset))

        rp1=unitcell<<rect_partialetch

        rp2=unitcell<<rect_partialetch

        rp2.move(destination=(self.pitch,0))

        r2 = unitcell << rect

        r2.move(origin=o.coord,\
        destination=(o+Point(self.pitch,self.y_offset)).coord)

        r3= unitcell<< rect

        r3.move(origin=o.coord,\
            destination=(o+Point(2*self.pitch,0)).coord)

        unitcell.absorb(r2)

        unitcell.absorb(r3)

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

        b_main=Bus()

        b_main.origin=o

        b_main.layer=self.layer

        b_main.size=Point(self.x,self.active_area.y)

        b_main.distance=Point(self.active_area.x+self.x,0)

        main_etch=b_main.draw()

        etch=Device(self.name)

        etch.absorb(etch<<main_etch)

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

        del main_etch

        return etch

class Anchor(LayoutPart):
    ''' Generates anchor structure.

    Derived from LayoutPart.

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


            # print(f"""Metalized X portion of anchor {self.metalized.x} is larger than Anchor X Size {self.size.x}, capped to {self.size.x*0.9}\n""")
            self.metalized=Point(self.size.x*0.9,self.metalized.y)

        if self.metalized.y<=self.size.y:

            # print(f"""Metalized Y portion of anchor {self.metalized.y} is smaller than Anchor Y Size {self.size.y}, capped to {self.size.y*1.1}""")
            self.metalized=Point(self.metalized.x,self.size.y*1.1)

class Via(LayoutPart):
    ''' Generates via pattern.

    Derived from LayoutPart.

    Attributes
    ----------
    size : float
        if shape is 'rectangle', side of rectangle
        if shape is 'circle',diameter of cirlce

    shape : str (only 'rectangle' or 'circle')
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

class Routing(LayoutPart):
    ''' Generate automatic routing connection

    Derived from LayoutPart.

    Attributes
    ----------
    clearance : iterable of two coordinates
        bbox of the obstacle

    trace_width : float
        with of routing

    ports : list of two phidl.Ports
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

    clearance= LayoutParamInterface()

    side=LayoutParamInterface('left','right','auto')

    trace_width=LayoutParamInterface()

    ports=LayoutParamInterface()

    layer=LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.clearance=LayoutDefault.Routingclearance
        self.side=LayoutDefault.Routingside
        self.trace_width=LayoutDefault.Routingtrace_width
        self.ports=LayoutDefault.Routingports
        self.layer=LayoutDefault.Routinglayer

    def _draw_frame(self):

        rect=pg.bbox(self.clearance,layer=self.layer)
        rect.add_port(self.ports[0])
        rect.add_port(self.ports[1])
        rect.name=self.name+"frame"

        return rect

    def draw(self):

        p=self.path

        x=CrossSection()

        x.add(layer=self.layer,width=self.trace_width)

        try:

            path_cell=join(x.extrude(p,simplify=0.1))
            path_cell.name=self.name

        except Exception as e:

            print (e)

        return path_cell

    @property
    def path(self):

        def check_points(*points):

            for i,p in enumerate(points):

                if not isinstance(p,Point):

                    raise ValueError("wrong input")

                if i==0:

                    pass

                else:

                    p_ref=points[i-1]

                    dist=p-points[i-1]

                    if abs(dist)<self.trace_width/10:

                        p_new=p_ref+p*(self.trace_width/abs(p))

                        if not i==len(points)-1:

                            if points[i+1].x==p:

                                points[i+1]=Point(p_new.x,points[i+1].y)

                            elif points[i+1].y==p:

                                points[i+1]=Point(points[i+1].x,p_new.x)

                        points[i]=p_new

                out_list=[]

                for p in points:

                    out_list.append(p.coord)

                return out_list

        radius=0.1

        tol=1e-3

        bbox=pg.bbox(self.clearance)

        ll,lr,ul,ur=get_corners(bbox)

        source=self.ports[0]

        destination=self.ports[1]

        if source.y>destination.y:

            source=self.ports[1]
            destination=self.ports[0]

        if Point(source.midpoint).in_box(bbox.bbox) :

            raise ValueError(f" Source of routing {source.midport} is in clearance area {bbox.bbox}")

        if Point(destination.midpoint).in_box(bbox.bbox):

            raise ValueError(f" Destination of routing{destination.midpoint} is in clearance area{bbox.bbox}")

        if destination.y<=ll.y+tol  : # destination is below clearance

            if not(destination.orientation==source.orientation+180 or \
                destination.orientation==source.orientation-180):

                    raise Exception("Routing error: non-hindered routing needs +90 -> -90 oriented ports")

            distance=Point(destination.midpoint)-\
                Point(source.midpoint)

            p1=Point(source.midpoint)

            p2=p1+Point(distance.x,distance.y*(3/4))

            p3=p2+Point(0,distance.y/4)

            list_points=check_points(p1,p2,p3)

            try:

                p=pp.smooth(points=list_points,radius=radius,num_pts=30)

            except Exception:

                raise ValueError("error for non-hindered path ")

        else: #destination is above clearance

            if not destination.orientation==90 :

                raise ValueError("Routing case not covered yet")

            elif source.orientation==0 : #right ground_pad_side

                    source.name='source'

                    destination.name='destination'

                    p0=Point(source.midpoint)

                    p1=Point(ur.x+self.trace_width,p0.y)

                    p2=Point(p1.x,ur.y+self.trace_width)

                    p3=Point(destination.x,p2.y)

                    p4=Point(destination.x,destination.y)

                    list_points_rx=check_points(p0,p1,p2,p3,p4)

                    try:

                        p=pp.smooth(points=list_points_rx,radius=radius,num_pts=30)

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

                    list_points_lx=check_points(p0,p1,p2,p3,p4,p5)

                    try:

                        p_lx=pp.smooth(points=list_points_lx,radius=radius,num_pts=30)

                    except:

                        raise ValueError("error in +90 hindered tucked path, lx path")

                    #right path

                    p1=p0-Point(0,source.width/2)
                    p2=Point(lr.x+self.trace_width,p1.y)
                    p3=Point(p2.x,self.trace_width+destination.y)
                    p4=Point(destination.x,p3.y)
                    p5=Point(destination.x,destination.y)

                    list_points_rx=check_points(p0,p1,p2,p3,p4,p5)

                    try:

                        p_rx=pp.smooth(points=list_points_rx,radius=radius,num_pts=30)

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

                    list_points=check_points(p0,p1,p2,p3)

                    try:

                        p=pp.smooth(points=list_points,radius=radius,num_pts=30)#source tucked inside clearance

                    except Exception:

                        raise ValueError("error for non-tucked hindered p ,90 deg")

            elif source.orientation==180 : #left path

                p0=Point(source.midpoint)

                p1=Point(ll.x-self.trace_width,p0.y)

                p2=Point(p1.x,ur.y+self.trace_width)

                p3=Point(destination.x,p2.y)

                p4=Point(destination.x,destination.y)

                list_points_lx=check_points(p0,p1,p2,p3,p4)

                try:

                    p=pp.smooth(points=list_points_lx,radius=radius,num_pts=30)

                except Exception:

                    raise ValueError("error in +180 source, lx path")

        return p

    def _draw_with_frame(self):

        cell_frame=self._draw_frame()

        cell_frame.absorb(cell_frame<<self.draw())

        return cell_frame

    @property
    def resistance_squares(self):

        return self.path.length()/self.trace_width

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

            warnings.warn("Pad size too large, capped to pitch*2/3")

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

            warnings.warn("Pad size too large, capped to pitch*9/10")

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

class LFERes(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self._stretch_top_margin=False

        self._set_relations()

    def draw(self):

        self._set_relations()

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

    def export_params(self):

        self._set_relations()

        t=super().export_params()

        pop_all_dict(t,["IDT"+x for x in ["Name"]])

        pop_all_dict(t, ["Bus"+x for x in ['Name','DistanceX','DistanceY','SizeX']])

        pop_all_dict(t,["EtchPit"+x for x in['Name','ActiveAreaX','ActiveAreaY']])

        pop_all_dict(t,["Anchor"+x for x in ['Name','EtchX','XOffset','EtchChoice']])

        return t

    def import_params(self,df):

        super().import_params(df)

        self._set_relations()

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

        if self.anchor.metalized.x>self.bus.size.x:

            # warnings.warn(f"Anchor metal is too wide ({self.anchor.metalized.x}), reduced to {self.bus.size.x*0.9}")

            self.anchor.metalized=Point(\
                self.bus.size.x*0.9,\
                self.anchor.metalized.y)

    @property
    def resistance_squares(self):

        self._set_relations()

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

        self._set_relations()

        width=cell.xsize-2*self.etchpit.x

        height=cell.ysize-self.anchor.etch_margin.y-2*self.anchor.size.y

        return height/width

    @staticmethod
    def get_components():

        return {'IDT':IDT,"Bus":Bus,"EtchPit":EtchPit,"Anchor":Anchor}

class FBERes(LFERes):

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

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.bottomlayer=LayoutDefault.TFEResbottomlayer

    def draw(self):

        cell=Device(name=self.name)

        cell.add_ref(LFERes.draw(self))

        idt_bottom=copy(self.idt)

        idt_bottom.layer=self.bottomlayer

        idt_ref=cell<<idt_bottom.draw()

        p_bott=idt_ref.ports['bottom']

        p_bott_coord=Point(p_bott.midpoint)

        idt_ref.mirror(p1=(p_bott_coord-Point(p_bott.width/2,0)).coord,\
            p2=(p_bott_coord+Point(p_bott.width/2,0)).coord)

        idt_ref.move(origin=(idt_ref.xmin,idt_ref.ymax),\
            destination=(idt_ref.xmin,idt_ref.ymax+self.idt.length+self.idt.y_offset))

        bus_bottom=copy(self.bus)

        bus_bottom.layer=self.bottomlayer

        bus_ref=cell<<bus_bottom.draw()

        bus_ref.move(origin=(0,0),\
        destination=(0,-self.bus.size.y))

        cell.absorb(bus_ref)

        anchor_bottom=copy(self.anchor)

        anchor_bottom.layer=self.bottomlayer
        anchor_bottom.etch_choice=False

        anchor_ref=cell<<anchor_bottom.draw()

        anchor_ref.connect(anchor_ref.ports['conn'],\
            destination=idt_ref.ports['top'],\
            overlap=-self.bus.size.y)

        cell.absorb(anchor_ref)

        anchor_ref_2=cell<<anchor_bottom.draw()

        anchor_ref_2.connect(anchor_ref_2.ports['conn'],\
            destination=idt_ref.ports['bottom'],\
            overlap=-self.bus.size.y)

        cell.absorb(anchor_ref_2)

        cell.absorb(idt_ref)

        out_ports=cell.get_ports()

        for p in out_ports:

            cell.add_port(p)

        return cell

class MultiRouting(LayoutPart):

    sources=LayoutParamInterface()

    destinations=LayoutParamInterface()

    clearance=LayoutParamInterface()

    trace_width=LayoutParamInterface()

    layer=LayoutParamInterface()

    def __init__(self,*a,**k):

        super().__init__(*a,**k)

        self.sources=LayoutDefault.MultiRoutingsources
        self.destinations=LayoutDefault.MultiRoutingdestinations
        self.clearance=LayoutDefault.Routingclearance
        self.trace_width=LayoutDefault.Routingtrace_width
        self.layer=LayoutDefault.Routinglayer

    @property
    def paths(self):

        p=[]

        for s in self.sources:

            for d in self.destinations:

                r=self._create_routing(s,d)

                p.append(r.path)

        return p

    def _create_routing(self,s,d):

        r=Routing()

        r.trace_width=self.trace_width

        r.layer=self.layer

        r.side='auto'

        r.clearance=self.clearance

        if not all([isinstance(p, Port) for p in (s,d)]):

            raise TypeError(f"{p} is not a phidl Port")

        else:

            r.ports=(s,d,)

        return r

    def draw(self):

        c=Device(name=self.name)

        for s in self.sources:

            for d in self.destinations:

                r=self._create_routing(s,d)

                c<<r.draw()

        return c

_allclasses=(IDT,Bus,EtchPit,Anchor,Via,Routing,GSProbe,GSGProbe,Pad,MultiRouting,\
LFERes,FBERes,TFERes)

for cls in _allclasses:

    cls.draw=cached(cls)(cls.draw)

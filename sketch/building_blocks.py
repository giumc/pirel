from phidl.device_layout import Device, Port, DeviceReference, Group

import phidl.geometry as pg

from phidl import set_quickplot_options

from phidl import quickplot as qp

from phidl import Path,CrossSection

import os

import phidl.path as pp

import gdspy

import numpy as np

from abc import ABC, abstractmethod

from copy import copy,deepcopy

import matplotlib.pyplot as plt

import warnings

from pandas import Series,DataFrame

from layout_tools import *

ld=LayoutDefault()

class LayoutParam():

    def __init__(self,name,value):

        self._name=name
        self._value=value

    @property
    def label(self):

        import re

        return re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), self._name)

    def denormalize(self,val):

        return self._value*val

    @property
    def param(self):

        if not isinstance(self._value,Point):

            return {self.label:self._value}

        else:

            return {self.label+"X":self._value.x,self.label+"Y":self._value.y}

    @param.setter
    def param(self,df):

        if len(df)>1:

            raise ValueError("Pass a single element dict to set a LayoutParam")

        name=[*df][0]
        value=[*df.values()][0]

        if isinstance(self._value,Point):

            if name==self.label+"X":

                self._value.x=value

            elif name==self.label+"Y":

                self._value.y=value

        else:

            if name==self.label:

                self._value=value

class _LayoutParamInterface():

    def __init__(self,def_value=1):

        self._def_value=def_value

    def __set_name__(self,owner,name):

        self.public_name=name
        self.private_name="_"+name
        # self.__set__(owner,self._def_value)

    def __set__(self,owner,value):

        if not hasattr(owner,self.private_name):

                setattr(owner,self.private_name,LayoutParam(self.public_name,value))

                if not hasattr(owner,'_params_list'):

                    owner._params_list=[getattr(owner,self.private_name)]

                else:

                    owner._params_list.append(getattr(owner,self.private_name))

        else:

            oldvalue=getattr(owner,self.private_name)._value

            if isinstance(oldvalue,(int,float)) and isinstance(value,(int,float)):

                    old_param=getattr(owner,self.private_name)

                    old_param._value=value

            elif isinstance(oldvalue,str) and isinstance(value,str):

                    old_param=getattr(owner,self.private_name)

                    old_param._value=value

            elif isinstance(value,oldvalue.__class__):

                    old_param=getattr(owner,self.private_name)

                    old_param._value=value

            else:

                raise   ValueError("""Attempt to unlawful assingment between \n
                    type {} and type {} in LayoutParam {}""".format(oldvalue,value.__class__,self.public_name))

    def __get__(self,owner,objtype=None):

        if not hasattr(owner,self.private_name):

            # warnings.Warn("{} not correctly initialized".format(self.private_name))

            return self._def_value

        else:

            return getattr(owner,self.private_name)._value

class LayoutPart(ABC) :
    ''' Abstract class that implements features common to all layout classes.

        Attributes
        ---------

        name : str

            instance name
        origin : sketch.Point
            layout cell origin

        cell :  phidl.Device
            container of last generated cell

        text_params : property
            see help

    '''

    name=_LayoutParamInterface('default')

    def __init__(self,name='default',*args,**kwargs):
        ''' Constructor for LayoutPart.

        Parameters
        ----------

        name : str
            optional,default is 'default'.
        '''

        self.name=name

        self.origin=copy(ld.origin)

        self.cell=Device(name)

        self.text_params=copy(ld.TextParams)

    def view(self,blocking=True):
        ''' Visualize cell layout with current parameters.

        Parameters
        ----------
        blocking : boolean

            if true,block scripts until window is closed.
        '''

        set_quickplot_options(blocking=blocking)
        qp(self.draw())
        return

    def view_gds(self):
        ''' Visualize gds cell layout with current parameters.

        Blocks scripts excecution until figure is closed

        '''
        lib=gdspy.GdsLibrary('test')
        lib.add(self.draw())
        gdspy.LayoutViewer(lib)

    def print_params_name(self):
        ''' Print the available parameters to the class. '''

        df=self.export_params()

        print("List of parameters for instance of {}\n".format(self.__class__.__name__))

        print(*df.columns.values,sep='\n')

    def get_params_name(self):
        ''' Get a list of the available parameters in the class. '''

        df=self.export_params()

        return [*df.keys() ]

    def bbox_mod(self,bbox):
        ''' Default method that returns bbox for the class .

        Can be overridden by subclasses of LayoutPart that require customized
        bounding boxes.

        Parameters
        ---------

        bbox : iterable of 2 iterables of length 2
            lower left coordinates , upper right coordinates

        Returns
        ------
        bbox : iterable of two iterables of length 2
            lower left, upper right.
        '''

        msgerr="pass 2 (x,y) coordinates as a bbox"

        try :

            iter(bbox)

            for x in bbox:

                iter(x)

        except Exception:

            raise ValueError(msgerr)

        if not len(bbox)==2:

            raise ValueError(msgerr)


        if not all([len(x)==2 for x in bbox]):

            raise ValueError(msgerr)

        return bbox

    @property
    def text_params(self):
        ''' Attribute of LayoutPart.

        It controls how the text labels generated in LayoutPart.add_text() are
        formatted.

        It is a dict with the following keys:
            - 'font'        (if overridden, needs to be in sketch/ path)
            - 'size'        (int)
            - 'location'    ('left','right','top','bottom')
            - 'distance'    (sketch.Point)
            - 'label'       (string, can be multiline if '\\n' is added)
            - 'layer'       (int).
        '''

        if hasattr(self,'_text_params'):

            return self._text_params

        else :

            return ld.TextParams

    @text_params.setter
    def text_params(self,df):

        if not isinstance(df,dict):

            raise ValueError("text params is set by a dict")

        else:

            valid_names={'font','size','location','distance','label','layer'}

            for key in df.keys():

                if not key in valid_names:

                    raise ValueError("Invalid key for text_param.Valid options are :{}".format("\n".join(valid_names)))

                else:

                    self._text_params=df

    @abstractmethod
    def draw(self):
        ''' Draws cell based on current parameters.

        Abstract Method, to be implemented when subclassing.

        Returns
        -------
        cell : phidl.Device.
        '''
        pass

    def export_params(self):

        out_dict={}

        for param in self._params_list:

            if param.label in out_dict.keys():

                    raise ValueError("{} is a duplicate parameter name".format(paramdict.label))

            out_dict.update(param.param)

        return out_dict

    def import_params(self,df):
        ''' Pass to cell parameters in a DataFrame.

        Abstract Method, to be implemented when subclassing.

        Parameters
        ----------
        df : pandas.DataFrame
            parameter table, needs to be of length 1.
        '''

        for param in self._params_list:

            for name,value in df.items():

                param.param={name:value}

    @staticmethod
    def _add_columns(d1,d2):

        for cols in d2.columns:

            d1[cols]=d2[cols].iat[0]

        return d1

    @staticmethod
    def add_text(cell,text_opts=ld.TextParams):
        ''' Static method to add text to a cell.

        Parameters
        ---------

        cell : phidl.Device

        text_opts : LayoutPart.text_params

        Returns
        -------

        cell :phidl.Device.
        '''

        package_directory = os.path.dirname(os.path.abspath(__file__))

        font=os.path.join(package_directory,text_opts['font'])

        o=Point(0,0)

        ll,lr,ul,ur=get_corners(cell)

        text_cell=pg.text(size=text_opts['size'],\
            text=text_opts['label'],\
            font=font,\
            layer=text_opts['layer'])

        text_location=text_opts['location']

        text_size=Point().from_iter(text_cell.size)

        text_distance=text_opts['distance']

        if text_location=='top':

            o=ul+text_distance

        elif text_location=='bottom':

            o=ll-Point(0,text_size.y)-text_distance

        elif text_location=='right':

            o=ur+text_distance

            text_cell.rotate(angle=-90)

        elif text_location=='left':

            o=ll-text_distance

            text_cell.rotate(angle=90)

        text_ref=cell<<text_cell

        text_ref.move(origin=(0,0),\
            destination=o())

        cell.absorb(text_ref)

        del text_cell

        return cell

    def __repr__(self):

        df=Series(self.export_params())

        return df.to_string()

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

    length =_LayoutParamInterface()

    pitch = _LayoutParamInterface()

    y_offset =_LayoutParamInterface()

    coverage =_LayoutParamInterface()

    n =_LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.length=ld.IDT_y
        self.pitch=ld.IDTpitch
        self.y_offset=ld.IDTy_offset
        self.coverage=ld.IDTcoverage
        self.n=ld.IDTn
        self.layer=ld.IDTlayer

    def draw(self):
        ''' Generates layout cell based on current parameters.

        'top' and 'bottom' ports are included in the cell.

        Returns
        -------
        cell : phidl.Device.
        '''

        o=self.origin

        rect=pg.rectangle(size=(self.coverage*self.pitch,self.length),\
            layer=self.layer)

        rect.move(origin=(0,0),destination=o())

        unitcell=Device(self.name)

        r1=unitcell << rect
        unitcell.absorb(r1)
        r2 = unitcell << rect

        r2.move(origin=o(),\
        destination=(o+Point(self.pitch,self.y_offset))())

        r3= unitcell<< rect

        r3.move(origin=o(),\
            destination=(o+Point(2*self.pitch,0))())

        unitcell.absorb(r2)

        unitcell.absorb(r3)

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
        cell.add_port(Port(name='bottom',\
        midpoint=(o+\
        Point(midx,0))(),\
        width=totx,
        orientation=-90))

        cell.add_port(Port(name='top',\
        midpoint=(o+\
        Point(midx,self.length+self.y_offset))(),\
        width=totx,
        orientation=90))

        del unitcell,rect

        self.cell=cell

        return cell

    def get_finger_size(self):
        ''' get finger length and width.

        Returns
        -------
        size : sketch.Point
            finger size as coordinates lenght(length) and width(x).
        '''
        dy=self.length

        dx=self.pitch*self.coverage

        return Point(dx,dy)

    @property
    def active_area(self):

        return Point(self.pitch*(self.n*2+1),self.length+self.y_offset)

    def resistance(self,res_per_square=0.1):

        return res_per_square*self.length/self.pitch/self.coverage/self.n*2/3

    @classmethod
    def calc_n_fingers(self,c0_dens,z0,f,len):

        from numpy import ceil
        from math import pi

        return int(ceil(1/2/pi/f/c0_dens/z0/len))

class Bus(LayoutPart) :
    ''' Generates pair of bus structure.

    Derived from LayoutPart.

    Attributes
    ----------
    size : sketch.Point
        bus size coordinates of length(y) and width(x)
    distance : sketch.Point
        distance between buses coordinates
    layer : int
        bus layer.
    '''
    size=_LayoutParamInterface()

    distance=_LayoutParamInterface()

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
        o=self.origin

        pad=pg.rectangle(size=self.size(),\
        layer=self.layer).move(origin=(0,0),\
        destination=o())

        cell=Device(self.name)

        r1=cell<<pad
        cell.absorb(r1)
        r2=cell <<pad

        r2.move(origin=o(),\
        destination=(o+self.distance)())

        cell.absorb(r2)

        cell.add_port(name='conn',\
        midpoint=(o+Point(self.size.x/2,self.size.y))(),\
        width=self.size.x,\
        orientation=90)

        self.cell=cell

        del pad

        return cell

    def resistance(self,res_per_square=0.1):

        return res_per_square*self.size.x/self.size.y/2

class EtchPit(LayoutPart) :
    ''' Generates pair of etching trenches.

    Derived from LayoutPart.

    Attributes
    ----------
    active_area : sketch.Point
        area to be etched as length(Y) and width(X)
    x : float
        etch width
    layer : int
        etch pit layer
    '''

    active_area=_LayoutParamInterface()

    x=_LayoutParamInterface()

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
        midpoint=(o+Point(self.x+self.active_area.x/2,self.active_area.y))(),\
        width=self.active_area.x,\
        orientation=-90)

        port_down=Port('bottom',\
        midpoint=(o+Point(self.x+self.active_area.x/2,0))(),\
        width=self.active_area.x,\
        orientation=90)

        etch.add_port(port_up)
        etch.add_port(port_down)

        del main_etch

        self.cell=etch

        return etch

class Anchor(LayoutPart):
    ''' Generates anchor structure.

    Derived from LayoutPart.

    Attributes
    ----------
    size : sketch.Point
        length(Y) and size(X) of anchors

    etch_margin : sketch.Point
        length(Y) and size(X) of margin between
        etched pattern and metal connection

    etch_choice: boolean
        to add or not etching patterns

    etch_x : float
        width of etch pit

    layer : int
        metal layer

    etch_layer : int
        etch layer.
    '''

    size=_LayoutParamInterface()
    etch_margin=_LayoutParamInterface()
    etch_choice=_LayoutParamInterface()
    etch_x=_LayoutParamInterface()
    x_offset=_LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.size=copy(ld.Anchorsize)
        self.etch_margin=copy(ld.Anchoretch_margin)
        self.etch_choice=ld.Anchoretch_choice
        self.etch_x=ld.Anchoretch_x
        self.x_offset=ld.Anchorx_offset

        self.layer=ld.Anchorlayer
        self.etch_layer=ld.Anchoretch_layer

    def draw(self):
        ''' Generates layout cell based on current parameters.

        'conn' port is included in the cell.

        Returns
        -------
        cell : phidl.Device.
        '''
        if self.size.x<=self.etch_margin.x*2:

            warnings.warn("Malformed Anchor,device will be fixed")

            self.size.x=self.size.x+self.etch_margin.x*2

        o=self.origin

        anchor=pg.rectangle(\
            size=(self.size-Point(2*self.etch_margin.x,0))(),\
            layer=self.layer)

        etch_size=Point(\
        (self.etch_x-self.size.x)/2,\
        self.size.y-2*self.etch_margin.y)

        offset=Point(self.x_offset,0)

        cell=Device(self.name)

        etch_sx=pg.rectangle(\
            size=(etch_size-offset)(),\
            layer=self.etch_layer)

        etch_dx=pg.rectangle(\
            size=(etch_size+offset)(),\
            layer=self.etch_layer)

        etch_sx_ref=(cell<<etch_sx).move(origin=(0,0),\
        destination=(o+Point(0,self.etch_margin.y))())

        anchor_transl=o+Point(etch_sx.size[0]+self.etch_margin.x,0)

        anchor_ref=(cell<<anchor).move(origin=(0,0),\
        destination=anchor_transl())

        etchdx_transl=anchor_transl+Point(anchor.size[0]+self.etch_margin.x,self.etch_margin.y)

        etch_dx_ref=(cell<<etch_dx).move(origin=(0,0),\
        destination=etchdx_transl())

        cell.add_port(name='conn',\
        midpoint=(anchor_transl+Point(self.size.x/2-self.etch_margin.x,self.size.y))(),\
        width=self.size.x-2*self.etch_margin.x,\
        orientation=90)

        if self.etch_choice==True:

            cell.absorb(etch_sx_ref)
            cell.absorb(anchor_ref)
            cell.absorb(etch_dx_ref)

        else:

            cell.remove(etch_sx_ref)
            cell.remove(etch_dx_ref)

        self.cell=cell

        del anchor, etch_sx,etch_dx

        return cell

    def resistance(self,res_per_square=0.1):

        return res_per_square*self.size.y/self.size.x

class Via(LayoutPart):
    ''' Generates via pattern.

    Derived from LayoutPart.

    Attributes
    ----------
    size : float
        if type is 'rectangle', side of rectangle
        if type is 'circle',diameter of cirlce

    type : str (only 'rectangle' or 'circle')
        via shape
    layer : int
        via layer.
    '''
    size=_LayoutParamInterface()

    type=_LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=ld.Vialayer
        self.type=ld.Viatype
        self.size=ld.Viasize

    def draw(self):

        if self.type=='square':

            cell=pg.rectangle(size=(self.size,self.size),\
                layer=self.layer)

        elif self.type=='circle':

            cell=pg.circle(radius=self.size/2,\
            layer=self.layer)

        else:

            raise ValueError("Via Type can be \'square\' or \'circle\'")
        cell.move(origin=(0,0),\
            destination=self.origin())

        cell.name=self.name

        cell.add_port(Port(name=self.name,\
        midpoint=cell.center,\
        width=cell.xmax-cell.xmin,\
        orientation=90))

        self.cell=cell

        return cell

class Routing(LayoutPart):
    ''' Generate automatic routing connection

    Derived from LayoutPart.

    Arguments
    ---------
    side : str (default 'auto')
        decides where to go if there is an obstacle in the routing,
        only 'auto','left','right'

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

    layer : int
        metal layer.
    '''

    trace_width=_LayoutParamInterface()

    def __init__(self,side='auto',*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.layer=ld.Routinglayer
        self.trace_width=ld.Routingtrace_width
        self.clearance=ld.Routingclearance
        self.ports=ld.Routingports
        self.side=side

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self,new_side):
        valid_names={'auto','left','right'}
        if new_side.lower() in valid_names:

            self._side=new_side.lower()

        else:

            raise ValueError("Routing side can be {}".format(\
            "or ".join(valid_names)))

    def draw_frame(self):

        rect=pg.bbox(self.clearance,layer=self.layer)
        rect.add_port(self.ports[0])
        rect.add_port(self.ports[1])
        rect.name=self.name+"frame"

        return rect

    def draw(self):

        cell=Device(self.name)

        bbox=pg.bbox(self.clearance)

        ll,_,_,ur=get_corners(bbox)

        source=self.ports[0]

        destination=self.ports[1]

        if source.y>destination.y:

            source=self.ports[1]
            destination=self.ports[0]

        y_overtravel=ll.y-source.midpoint[1]-self.trace_width

        taper_len=abs(min([y_overtravel,self.trace_width/4]))

        if destination.y<=ll.y : # destination is below clearance

            if not(destination.orientation==source.orientation+180 or \
                destination.orientation==source.orientation-180):

                    raise Exception("Routing error: non-hindered routing needs +90 -> -90 oriented ports")

            # source=self._add_taper(cell,source,len=taper_len)
            # destination=self._add_taper(cell,destination,len=self.trace_width/4)

            source.name='source'
            destination.name='destination'

            distance=Point().from_iter(destination.midpoint)-\
                Point().from_iter(source.midpoint)

            p0=Point().from_iter(source.midpoint)

            p1=p0+Point(0,distance.y/3)

            p2=p1+Point(distance.x,distance.y/3)

            p3=p2+Point(0,distance.y/3)

            list_points=np.array([p0(),p1(),p2(),p3()])

            path=pp.smooth(points=list_points)

        else: #destination is above clearance

            if not destination.orientation==90 :

                raise ValueError("Routing case not covered yet")

            if source.orientation==90 :

                ll,lr,ul,ur=get_corners(bbox)

                if source.x+self.trace_width>ll.x and source.x-self.trace_width<lr.x: #source tucked inside clearance

                    # if self.side=='auto':

                        # source=self._add_taper(cell,source,len=taper_len)
                        # destination=self._add_taper(cell,destination,len=self.trace_width/4)

                    # elif self.side=='left':

                        # source=self._add_ramp_lx(cell,source,len=taper_len)
                        # destination=self._add_taper(cell,destination,len=self.trace_width/4)

                    # elif self.side=='right':

                        # source=self._add_ramp_rx(cell,source,len=taper_len)
                        # destination=self._add_taper(cell,destination,len=self.trace_width/4)

                    source.name='source'
                    destination.name='destination'

                    p0=Point().from_iter(source.midpoint)

                    center_box=Point().from_iter(bbox.center)

                    #left path
                    p1=p0+Point(0,y_overtravel)
                    p2=Point(ll.x-self.trace_width,p1.y)
                    p3=Point(p2.x,self.trace_width+destination.y)
                    p4=Point(destination.x,p3.y)
                    p5=Point(destination.x,destination.y)

                    list_points_lx=[p0(),p1(),p2(),p3(),p4(),p5()]

                    path_lx=pp.smooth(points=list_points_lx)
                    #right path
                    p1=p0+Point(0,y_overtravel)
                    p2=Point(lr.x+self.trace_width,p1.y)
                    p3=Point(p2.x,self.trace_width+destination.y)
                    p4=Point(destination.x,p3.y)
                    p5=Point(destination.x,destination.y)

                    list_points_rx=[p0(),p1(),p2(),p3(),p4(),p5()]

                    path_rx=pp.smooth(points=list_points_rx)

                    if self.side=='auto':

                        if path_lx.length()<path_rx.length():

                            path=path_lx

                        else:

                            path=path_rx

                    elif self.side=='left':

                        path=path_lx

                    elif self.side=='right':

                        path=path_rx

                    else:

                        raise Exception("Invalid option for side :{}".format(self.side))

                else:

                    # source is not tucked under the clearance

                    source=self._add_taper(cell,source,len=self.trace_width/4)
                    destination=self._add_taper(cell,destination,len=self.trace_width/4)

                    source.name='source'
                    destination.name='destination'

                    p0=Point().from_iter(source.midpoint)

                    ll,lr,ul,ur=get_corners(bbox)

                    y_overtravel=ll.y-p0.y

                    center_box=Point().from_iter(bbox.center)

                    #left path
                    p1=Point(p0.x,destination.y+self.trace_width)
                    p2=Point(destination.x,p1.y)
                    p3=Point(destination.x,destination.y)

                    list_points=[p0(),p1(),p2(),p3()]

                    path=pp.smooth(points=list_points)#source tucked inside clearance

            elif source.orientation==0 : #right path
                    source=self._add_taper(cell,source,len=-taper_len)
                    source.name='source'
                    destination.name='destination'

                    p0=Point().from_iter(source.midpoint)


                    p1=Point(ur.x+self.trace_width,p0.y)
                    p2=Point(p1.x,ur.y+self.trace_width)
                    p3=Point(destination.x,p2.y)
                    p4=Point(destination.x,destination.y)
                    list_points_rx=[p0(),p1(),p2(),p3(),p4()]

                    path=pp.smooth(points=list_points_rx)

            elif source.orientation==180 : #left path
                    source=self._add_taper(cell,source,len=-taper_len)
                    source.name='source'
                    destination.name='destination'

                    p0=Point().from_iter(source.midpoint)


                    p1=Point(ll.x-self.trace_width,p0.y)
                    p2=Point(p1.x,ur.y+self.trace_width)
                    p3=Point(destination.x,p2.y)
                    p4=Point(destination.x,destination.y)

                    list_points_lx=[p0(),p1(),p2(),p3(),p4()]

                    path=pp.smooth(points=list_points_lx)

        x=CrossSection()

        x.add(layer=self.layer,width=self.trace_width)

        path_cell=x.extrude(path,simplify=5)

        cell.absorb(cell<<path_cell)

        cell=join(cell)

        del path_cell

        del bbox

        self.cell=cell

        return cell

    def _add_taper(self,cell,port,len=10):

        if not(port.width==self.trace_width):

            taper=pg.taper(length=len,\
            width1=port.width,width2=self.trace_width,\
            layer=self.layer)

            taper_ref=cell<<taper

            taper_port=taper.ports[1]

            taper_port.orientation=taper_port.orientation+180
            taper_ref.connect(taper_port,
            port)

            taper_ref.rotate(angle=180,center=port.center)

            port=taper_ref.ports[2]

            cell.absorb(taper_ref)

            del taper

        return port

    def _add_ramp_lx(self,cell,port,len=10):

        if not(port.width==self.trace_width):

            taper=pg.ramp(length=len,\
            width1=port.width,width2=self.trace_width,\
            layer=self.layer)

            taper_ref=cell<<taper

            taper_port=taper.ports[1]

            taper_port.orientation=taper_port.orientation+180

            taper_ref.connect(taper_port,
            port)

            taper_ref.rotate(angle=180,center=port.center)

            port=taper_ref.ports[2]

            cell.absorb(taper_ref)

            del taper

        return port

    def _add_ramp_rx(self,cell,port,len=10):

            if not(port.width==self.trace_width):

                taper=pg.ramp(length=len,\
                width1=port.width,width2=self.trace_width,\
                layer=self.layer)

                taper_ref=cell<<taper

                taper_ref.mirror(p1=(0,0),p2=(0,1))

                taper_port=taper.ports[1]

                taper_port.orientation=taper_port.orientation+180

                taper_ref.connect(taper_port,
                port)

                port=taper_ref.ports[2]

                cell.absorb(taper_ref)

                del taper

            return port

    def draw_with_frame(self):

        cell_frame=self.draw_frame()

        cell_frame.add(self.draw())

        return cell_frame

    def resistance(self,res_per_square=0.1):

        return res_per_square*self.draw().area/self.trace_width

class GSProbe(LayoutPart):
    ''' Generates GS pattern.

    Derived from LayoutPart.

    Attributes
    ----------
    size : float
        if type is 'rectangle', side of rectangle
        if type is 'circle',diameter of cirlce

    pitch : float
        probe pitch

    layer : int
        via layer.
    '''

    pitch=_LayoutParamInterface()
    size=_LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=ld.GSProbelayer
        self.pitch=ld.GSProbepitch
        self.size=copy(ld.GSProbesize)

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

        cell=Device(self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell
        pad_sig.move(origin=o(),\
        destination=(o+dp)())

        cell.add_port(Port(name='gnd_left',\
        midpoint=(o+Point(pad_x/2+self.pitch,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name='sig',\
        midpoint=(o+Point(pad_x/2,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        self.cell=cell

        return cell

class GSGProbe(LayoutPart):
    ''' Generates GSG pattern.

    Derived from LayoutPart.

    Attributes
    ----------
    size : float
        if type is 'rectangle', side of rectangle
        if type is 'circle',diameter of cirlce

    pitch : float
        probe pitch

    layer : int
        via layer.
    '''

    pitch=_LayoutParamInterface()
    size=_LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=ld.GSGProbelayer
        self.pitch=ld.GSGProbepitch
        self.size=copy(ld.GSGProbesize)

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
        destination=o())

        cell=Device(self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell
        pad_sig.move(origin=o(),\
        destination=(o+dp)())

        pad_gnd_dx=cell<<pad_cell
        pad_gnd_dx.move(origin=o(),\
        destination=(o+dp*2)())

        cell.add_port(Port(name='sig',\
        midpoint=(o+Point(pad_x/2+self.pitch,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name='gnd_left',\
        midpoint=(o+Point(pad_x/2,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name='gnd_right',\
        midpoint=(o+Point(pad_x/2+2*self.pitch,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        self.cell=cell

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

    size=_LayoutParamInterface()

    distance=_LayoutParamInterface()

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.size=ld.Padsize
        self.layer=ld.Padlayer
        self.distance=copy(ld.Paddistance)
        self.port=ld.Padport

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

        self.cell=r1

        return r1

    def resistance(self,res_per_square=0.1):

        return res_per_square*(1+self.distance/self.port.width)

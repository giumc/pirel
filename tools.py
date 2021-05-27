from abc import ABC, abstractmethod

from copy import copy,deepcopy

import numpy as np

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray,Device

from pandas import Series,DataFrame

from phidl import set_quickplot_options

from phidl import quickplot as qp

import warnings

import re

class Point:
    ''' Handles 2-d coordinates.

    Arguments
    --------
    x : float
    y : float.
    '''

    def __init__(self,*a):

        if len(a)==1:

            if len(a[0])==2:

                self._x=a[0][0]*1.0
                self._y=a[0][1]*1.0

            else:

                raise ValueError("Bad point assignment")

        elif len(a)==2:

            self._x=a[0]*1.0
            self._y=a[1]*1.0

        else:

                raise ValueError("Bad point assignment")

    @property
    def coord(self):
        ''' returns coordinates in a 2-d tuple'''

        return (self.x,self.y)

    @property
    def x(self):

        return self._x

    @property
    def y(self):
        return self._y

    def in_box(self,bbox):

        tol=0
        ll=Point(bbox[0])
        ur=Point(bbox[1])

        if  self.x>ll.x-tol and\
            self.x<ur.x+tol and\
            self.y>ll.y+tol and\
            self.y<ur.y-tol:

                return True

        else:

            return False


    def __setattr__(self,name,value):

        if name in ('_x','_y'):

            super().__setattr__(name,value)

        else:

            raise AttributeError("Point is an immutable read-only")

    def __add__(self,p):

        if not isinstance(p,Point):

            raise Exception("cannote add Point to non Point")

        x1=self.x+p.x
        y1=self.y+p.y

        return Point(x1,y1)

    def __sub__(self,p):

        if not isinstance(p,Point):

            raise Exception("cannote sub Point to non Point")

        x1=self.x-p.x

        y1=self.y-p.y

        return Point(x1,y1)

    def __truediv__(self,x0):

        if isinstance(x0,int) or isinstance(x0,float):

            p=self
            x1=p.x/x0
            y1=p.y/x0

            return Point(x1,y1)

        else:

            raise Exception("Division Point/x0 is not possible here")

    def __repr__(self):

        return f"x={self.x} y ={self.y}"

    __radd__ = __add__

    def __mul__(self,x0):

        if isinstance(x0,int) or isinstance(x0,float):

            x1=self.x*x0
            y1=self.y*x0

            return Point(x1,y1)

        else:

            raise Exception("Division Point/x0 is not possible here")

    def __eq__(self,p2):

        if not isinstance(p2,Point):

            raise ValueError(f"cannot compare Point and {p2.__class__}")

        else:

            if self.x==p2.x and self.y==p2.y:

                return True

            else:

                return False

    __rmul__=__mul__

    def __hash__(self):

        return hash(self.coord)

    def __abs___(self):

        return sqrt(self.x^2+self.y^2)

class LayoutDefault:
    '''container of pirel constants.'''

    origin=Point(0,0)
    layerSi = 0
    layerBottom = 1
    layerTop = 2
    layerPad = 3
    layerEtch = 4
    layerVias = 5
    layerPartialEtch = 6
    layerBackSide = 7
    layerMask = 99

    #text

    TextParams={'font':"BebasNeue-Regular.otf",'size':125.0,'location':'top',\
        'distance':Point(0,100),'label':"default",'layer':layerTop}

    #IDT

    IDT_y = 200.0
    IDTpitch = 8.0
    IDTcoverage = 0.7
    IDTy_offset = 10.0
    IDTlayer = layerTop
    IDTn = 40

    #Bus

    Bussize=Point(IDTpitch*2*IDTn,IDTpitch*2)
    Busdistance=Point(0,IDT_y+IDTy_offset)

    #EtchPit

    EtchPit_x=Bussize.x/4
    EtchPitactive_area=Point(Bussize.x,\
        IDT_y+IDTy_offset+2*Bussize.y)
    EtchPitlayer=layerEtch

    #Anchor
    Anchorsize=Point(IDTpitch*IDTn/4,\
        2*Bussize.y)
    Anchor_metalized=Point(Anchorsize.x-4,Anchorsize.y+4)
    Anchoretch_x=EtchPit_x
    Anchorx_offset=0.0
    Anchorlayer=IDTlayer
    Anchoretch_layer=EtchPitlayer
    Anchoretch_choice=True

    #LFERes
    LFEResactive_area_margin=0.5
    #FBERes

    FBEResplatelayer=layerBottom
    #GSProbe
    GSProbepitch = 150.0
    GSProbepad_size = Point(80,80)

    GSProbelayer = layerTop
    GSProberouting = True
    GSProbespacing = Point(20,30)

    #Via

    Vialayer=layerVias
    Viashape='circle'
    Viasize=5

    #GSGProbe

    GSGProbelayer=layerTop
    GSGProbepitch=200.0
    GSGProbesize=Point(100,100)

    GSProbelayer=GSGProbelayer
    GSProbepitch=GSGProbepitch
    GSProbesize=GSGProbesize
    
    #TFERes

    TFEResbottomlayer=layerBottom

    #Routing

    Routingtrace_width=80.0

    Routingclearance=((0,250),(300,550))

    Routinglayer=layerTop

    Routingports=(Port(name='1',midpoint=(450,0),\
        width=50,orientation=90),\
            Port(name='2',midpoint=(100,550),\
            width=50,orientation=90),)

    Routingside='auto'

    #MultiRouting

    MultiRoutingsources=(Routingports[0],)
    MultiRoutingdestinations=(Port(name='2',midpoint=(100,550),\
        width=50,orientation=90),\
            Port(name='3',midpoint=(200,80),\
            width=50,orientation=-90))
    #GSGProbe_LargePad
    GSGProbe_LargePadground_size=200.0

    #ParametricArray

    Arrayx_spacing=50.0
    Arrayx_param={"IDTPitch":[_ for _ in range(1,4)]}
    Arraylabels_top=["IDTP"+str(x) for x in range(1,4)]
    Arraylabels_bottom=[str(x) for x in range(1,4)]

    #ParametricMatrix
    Matrixy_param={"IDTLength":[_ for _ in range(100,400,100)]}
    Matrixy_spacing=Arrayx_spacing
    Matrixlabels_top=[ ["IDTP"+str(x)+y for x in range(1,4)]\
        for y in ["L"+str(z) for z in range(100,400,100)]]
    Matrixlabels_bottom=[ [str(x)+str(y) for x in range(1,4)] \
        for y in range(100,400,100)]

    #Stack
    Stackn=4

    #Pad

    Padsize=400.0
    Padlayer=IDTlayer
    Paddistance=200.0
    Padport=Port(name='top',midpoint=(50,50),width=100,\
        orientation=-90)

    #array

    arraybusextlength=30.0

class _LayoutParam:

    def __init__(self,name,value):

        self._name=name
        self._value=value

    @property
    def label(self):

        import re

        return re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), self._name)

    @property
    def param(self):

        if not isinstance(self._value,Point):

            return {self.label:self._value}

        else:

            return {self.label+"X":self._value.x,self.label+"Y":self._value.y}

    @property
    def value(self):

        return self._value

    @value.setter
    def value(self,new_value):

        if isinstance(self.value,float):

            if isinstance(new_value,(int,float)):

                self._value=new_value*1.0

        elif self.value.__class__==new_value.__class__:

            self._value=new_value

        else:

            raise ValueError(f"Cannot assign type {new_value.__class__} to {self.label}")

    @property
    def x(self):

        return self.__get_coord('x')

    @property
    def y(self):

        return self.__get_coord('y')

    @x.setter
    def x(self,value):

        self.__set_coord('x',value)

    @y.setter
    def y(self,value):

        self.__set_coord('y',value)

    def __get_coord(self,type):

        if isinstance(self.value,Point):

            if not type in ('x','y'):

                raise ValueError("Coordinate should be either {}".format(" or".join(('x','y'))))

            else:

                return getattr(self.value,type)

        else:

            raise ValueError(f"{self.value} is not a {Point.__class__}, so you can't get {type}")

    def __set_coord(self,type,value):

        if isinstance(self.value,Point):

            if not type in ('x','y'):

                raise ValueError("Coordinate should be either {}".format(" or".join(('x','y'))))

            else:

                return setattr(self.value,type,value)

        else:

            raise ValueError(f"{self.value} is not a {Point.__class__}, so you can't set {type}")

    def __repr__(self):
        return str(self.param)

    __str__=__repr__

class LayoutParamInterface:

    def __init__(self,*args):

        if args:

            self.constraints=args

        else :

            self.constraints=None

    def __set_name__(self,owner,name):

        self.public_name=name
        self.private_name="_"+name

    def __set__(self,owner,new_value):

        if self.constraints is not None:

            if not new_value in self.constraints:

                raise ValueError(f""" Value {new_value} is not legal for attribute {self.public_name}\n
                            legal values are {self.constraints}""")

        if not hasattr(owner,self.private_name):

            new_param=_LayoutParam(self.public_name,new_value)

            setattr(owner,self.private_name,new_param)

            if not hasattr(owner.__class__,'_params_dict'):

                setattr(owner.__class__,'_params_dict',{new_param.label:self.private_name})

            else:

                old_dict=getattr(owner.__class__,'_params_dict')

                if not new_param.label in old_dict:

                    old_dict.update({new_param.label:self.private_name})

        else:

            old_param=getattr(owner,self.private_name)

            old_param.value=new_value

    def __get__(self,owner,objtype=None):

        if not hasattr(owner,self.private_name):

            raise ValueError(f"{self.public_name} not in {owner.__class__}")

        else:

            return getattr(owner,self.private_name).value

class LayoutPart(ABC) :
    ''' Abstract class that implements features common to all layout classes.

        Attributes
        ---------

        name : str

            instance name
        origin : PyResLayout.Point
            layout cell origin

        cell :  phidl.Device
            container of last generated cell

        text_params : property
            see help

    '''
    name=LayoutParamInterface()

    def __init__(self,name='default',*args,**kwargs):
        ''' Constructor for LayoutPart.

        Parameters
        ----------

        label : str
            optional,default is 'default'.
        '''

        self.__class__._params_dict={}

        self.name=name

        self.origin=LayoutDefault.origin

        for p,cls in self.get_components().items():

            setattr(self,p.lower(),cls(name=self.name+p))

        # self.__class__.draw=cached(self.__class__.draw)

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

    def _bbox_mod(self,bbox):
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

        return (Point(bbox[0]).coord,Point(bbox[1]).coord)

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

        param_dict=self._params_dict

        out_dict={}

        for p,c in self.get_components().items():

            component_params=getattr(self,p.lower()).export_params()

            for name,value in component_params.items():

                if not name=='Type':

                    out_dict.update({p+name:value})

        for param_name in param_dict.values():

            if not hasattr(self,param_name):

                import pdb; pdb.set_trace()

                raise AttributeError(f" no {param_name} in {self.__class__.__name__}")

            else:

                out_dict.update(getattr(self,param_name).param)

        out_dict.update({"Type":self.__class__.__name__})

        return out_dict

    def import_params(self,df):
        ''' Pass to cell parameters in a dict.

        Parameters
        ----------
        df : dict.
        '''

        for name in self.get_components().keys():

            if_match_import(getattr(self,name.lower()),df,name)

        for param_label,param_key in self._params_dict.items():

            param_key=param_key.lstrip("_")

            if param_label in df.keys():

                if callable(df[param_label]):

                    setattr(self,param_key,df[param_label]())

                else :

                     setattr(self,param_key,df[param_label])

            if param_label+'X' in df.keys():

                old_point=getattr(self,param_key)

                if callable(df[param_label+"X"]):

                    setattr(self,param_key,Point(df[param_label+"X"](),old_point.y))

                else:

                    setattr(self,param_key,Point(df[param_label+"X"],old_point.y))

            if param_label+'Y' in df.keys():

                old_point=getattr(self,param_key)

                if callable(df[param_label+"Y"]):

                    setattr(self,param_key,Point(old_point.x,df[param_label+"Y"]()))

                else:

                    setattr(self,param_key,Point(old_point.x,df[param_label+"Y"]))

    def export_all(self):

        df=self.export_params()

        if hasattr(self,'resistance_squares'):

            df["Resistance"]=self.resistance_squares

        modkeys=[*df.keys()]

        pop_all_match(modkeys,".*Layer*")

        pop_all_dict(df,[item for item in [*df.keys()] if item not in modkeys])

        return df

    @staticmethod
    def get_components():

        return {}

    def __getattr__(self,name):

        for p , c in self.get_components().items():

            if name.startswith(p):

                return getattr(getattr(self,p.lower()),name.replace(p,""))

        else:

            raise AttributeError(f"No attribute {name} in {self.__class__.__name__} ")

    def __repr__(self):

        df=Series(self.export_all())

        return df.to_string()

def add_compass(device : Device) -> Device:
    ''' add four ports at the bbox of a cell.

    Parameters
    ----------
    device : phidl.Device

    Returns
    -------
    device : phidl.Device.
    '''

    bound_cell=pg.compass(size=device.size).move(\
    origin=(0,0),destination=device.center)

    ports=port=bound_cell.get_ports()

    device.add_port(port=ports[0],name='N')
    device.add_port(port=ports[1],name='S')
    device.add_port(port=ports[2],name='E')
    device.add_port(port=ports[3],name='W')

    return device

def draw_array(cell : Device, x : int, y : int, \
    row_spacing : float = 0 , column_spacing : float = 0 ) -> Device:
    ''' returns a spaced matrix of identical cells.

        draw_array() preserves ports in the original cells
    Parameters
    ----------
    cell : phidl.Device

    x : int
        columns of copies
    y : int
        rows of copies

    row_spacing: float
    column_spacing: float

    Returns
    -------

    cell : phidl.Device.
    '''

    new_cell=pg.Device(cell.name+"array")

    cell_size=Point(cell.size)+Point(column_spacing,row_spacing)

    cellmat=[]

    ports=[]

    for j in range(y):

        cellvec=[]

        for i in range(x):

            cellvec.append(new_cell.add_ref(cell,alias=cell.name+str(i)+str(j)))

            cellvec[i].move(
                destination=(Point(cell_size.x*i,cell_size.y*j)).coord)

            for p in cellvec[i].ports.values():

                ports.append(Port(name=p.name+str(i),\
                    midpoint=p.midpoint,\
                    width=p.width,\
                    orientation=p.orientation))

        cellmat.append(cellvec)

    for p in ports:

        new_cell.add_port(p)

    del cellmat

    return new_cell

def print_ports(device : Device):
    ''' print a list of ports in the cell.

    Parameters
    ----------
    device : phidl.Device.
    '''

    for i,p in enumerate(device.get_ports()):

        print(i,p,'\n')

def join(device : Device) -> Device:
    ''' returns a copy of device with all polygons joined.

    Parameters
    ----------
    device : phidl.Device.
    '''
    out_cell=pg.union(device,by_layer=True, precision=0.001,join_first=False)

    return out_cell

def get_corners(device : Device) :
    ''' get corners of a device.

    Parameters
    ---------
    device : phidl.Device

    Returns:
    ll : sketch.Point
        lower left

    lr : sketch.Point
        lower right

    ul : sketch.Point
        upper left

    ur : sketch.Point
        upper right.
    '''
    bbox=device.bbox
    ll=Point(bbox[0,0],bbox[0,1])
    lr=Point(bbox[1,0],bbox[0,1])
    ul=Point(bbox[0,0],bbox[1,1])
    ur=Point(bbox[1,0],bbox[1,1])

    return ll,lr,ul,ur

def check(device : Device):
    ''' Shows the device layout.

    Blocks script until window is closed.
    '''
    set_quickplot_options(blocking=True)
    qp(device)

def if_match_import(obj : LayoutPart ,param : dict, tag : str ):
    ''' used to load data in subclasses.

    Parameters
    ---------
    obj : LayoutPart
        a instance that might contain parameters in 'df'

    param : dict

    tag : str

    Use:
        if_match_import() looks for 'tag' in 'param' string;
        if 'tag' is found in a key of 'param',
        'tag' it is removed from that key,
        A copy of 'param' with 'param' key changed into the new string
        is passed to obj.import_params().
    '''

    from re import search

    for name,value in param.items():

        match=search(tag,name)

        if match and match.start()==0:

            varname=name.replace(tag,"")

            obj.import_params({varname:value})

def add_prefix_dict(old_dict,tag) -> dict:

    new_dict={}

    for name in old_dict.keys():

        new_dict[tag+name]=old_dict[name]

    return new_dict

def pop_all_dict(old_dict : dict ,elems : list):

    for el in elems:

        old_dict.pop(el)

def pop_all_match(l : list , reg : str) -> list:

    from re import compile

    r=compile(reg)

    [l.remove(x) for x in filter(r.match,l)]

    return l

def parallel_res(*args) -> float:

    sum_y=0

    for arg in args:

        sum_y=sum_y+1/arg

    return 1/sum_y

def get_class_param(cls : LayoutPart.__class__ ) -> list:

    out_list=[]

    if hasattr(cls,'_params_dict'):

        for p in cls._params_dict.values():

                out_list.append(p.lstrip('_'))

    for p,c in cls.get_components().items():

        [out_list.append(p+x) for x in get_class_param(c)]

    return out_list

def cached(cls):

    def cache_dec(fun):

        from functools import wraps

        @wraps(fun)

        def wrapper(self):

            params=get_class_param(cls)

            pop_all_match(params,'.*name*')

            dict_name="_"+fun.__name__+"_lookup"

            paramhash=_get_hashable_params(self,params)

            if not hasattr(cls,dict_name):

                setattr(cls,dict_name,{})

            dict_lookup=getattr(cls,dict_name)

            if paramhash in dict_lookup.keys():

                return dict_lookup[paramhash]

            else:

                xout=fun(self)

                dict_lookup[paramhash]=xout

                return xout

        return wrapper

    return cache_dec

def attach_taper(cell : Device , port : Port , length : float , \
    width2 : float, layer=LayoutDefault.layerTop) :

    t=pg.taper(length=length,width1=port.width,width2=width2,layer=layer)

    t_ref=cell.add_ref(t)

    t_ref.connect(1,destination=port)

    new_port=t_ref.ports[2]

    new_port.name=port.name

    cell.absorb(t_ref)

    cell.remove(port)

    cell.add_port(new_port)

def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return str(msg) + '\n'

def _get_hashable_params( obj : LayoutPart , params : list) ->tuple:

    paramdict={}

    for name in params:

        value=getattr(obj,name)

        try:

            port_list=tuple([(p.name,Point(p.midpoint).coord,p.width,p.orientation) for p in value])

            paramdict.update({name:port_list})

        except Exception:

            paramdict.update({name:value})

    return tuple(paramdict.items())

warnings.formatwarning = custom_formatwarning

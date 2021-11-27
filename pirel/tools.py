from abc import ABC, abstractmethod

import numpy as np

from pandas import Series,DataFrame

from phidl import set_quickplot_options

from phidl import quickplot as qp

import warnings, re, pathlib, gdspy, pdb, functools, inspect

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray,Device,DeviceReference

import phidl.device_layout as dl

from IPython import get_ipython

if get_ipython() is not None:

    import matplotlib.pyplot as plt

    get_ipython().run_line_magic('matplotlib', 'inline')

    plt.rcParams["figure.figsize"]=15,15

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

                if  (isinstance(a[0][0],int) or isinstance(a[0][0],float)) and (isinstance(a[0][1],int) or isinstance(a[0][1],float) ):

                    self._x=a[0][0]*1.0
                    self._y=a[0][1]*1.0

                else:

                    raise ValueError("Bad point assignment")

            else:

                raise ValueError("Bad point assignment")

        elif len(a)==2:

            if (isinstance(a[0],int) or isinstance(a[0],float)) and (isinstance(a[1],int) or isinstance(a[1],float)):

                self._x=a[0]*1.0
                self._y=a[1]*1.0

            else:

                raise ValueError("Bad point assignment")


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

        tol=1e-3
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

            raise Exception(f"cannote add Point to {p}")

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

            raise ValueError("Point dividion is only possible to a scalar")

    def __repr__(self):

        return f"x={self.x} y ={self.y}"

    __radd__ = __add__

    def __mul__(self,x0):

        if isinstance(x0,int) or isinstance(x0,float):

            x1=self.x*x0
            y1=self.y*x0

            return Point(x1,y1)

        else:

            raise ValueError("Point multiplication is only possible to a scalar")

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

    def __abs__(self):

        from math import sqrt

        return sqrt(self.x**2+self.y**2)

    def dot(self,b):

        if not isinstance(b,Point):

            raise ValueError(f"{b} needs to be a Point")

        return self.x*b.x+self.y*b.y

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
    IDTpitch = 20.0
    IDTcoverage = 0.7
    IDTy_offset = 10.0
    IDTlayer = layerTop
    IDTn = 4

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
    Viasize=20

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
    Routingoverhang=10.0

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

    Padsize=80.0
    Padlayer=IDTlayer
    Paddistance=30.0
    Padport=Port(name='top',midpoint=(50,50),width=100,\
        orientation=-90)

    #TwoPortProbe

    TwoPortProbeoffset=Point(0,200)

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

            raise ValueError(f"Cannot assign type {new_value.__class__.__name__} to {self.label}")

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
            layout cell origin.

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

    def view(self, gds=False,blocking=True,joined=False):
        ''' Visualize cell layout with current parameters.

        Parameters
        ----------
        blocking : boolean

            if true,block scripts until window is closed.

        gds : boolean

            if true, gdspy viewer is used.
            if false (default), phidl viewer is used.
        '''

        if gds:

            lib=gdspy.GdsLibrary()

            cell=lib.new_cell("Output")

            cell.add(gdspy.CellReference(self.draw()))

            cell.flatten()

            gdspy.LayoutViewer(lib)

        else:

            check(self.draw(),blocking=blocking,joined=joined)

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

    def get_params(self):
        ''' Returns a dict with param names : param values. '''

        param_dict=self._params_dict

        out_dict={}

        for p,c in self.get_components().items():

            component_params=getattr(self,p.lower()).get_params()

            for name,value in component_params.items():

                if not name=='Type':

                    out_dict.update({p+name:value})

        for param_name in param_dict.values():

            if not hasattr(self,param_name):

                raise AttributeError(f" no {param_name} in {self.__class__.__name__}")

            else:

                out_dict.update(getattr(self,param_name).param)

        out_dict.update({"Type":self.__class__.__name__})

        return out_dict

    def _set_params(self,df):

        for name in self.get_components().keys():

            if_match_import(getattr(self,name.lower()),df,name)

        for param_label,param_key in self._params_dict.items():

            param_key=param_key.lstrip("_")

            if param_label in df.keys():

                setattr(self,param_key,df[param_label])

            if param_label+'X' in df.keys():

                old_point=getattr(self,param_key)

                setattr(self,param_key,Point(df[param_label+"X"],old_point.y))

            if param_label+'Y' in df.keys():

                old_point=getattr(self,param_key)

                setattr(self,param_key,Point(old_point.x,df[param_label+"Y"]))

    def set_params(self,df):
        ''' Set instance parameters, passed from a dict.

        Parameters
        ----------
        df : dict.

            Note: dict value can be a function.
            In that case, it has to be function of self, so to set the parameter in a dynamic fashion.

        '''
        stable=False

        while not stable:

            pre_params=self.get_params()

            df_noncall={key:value for key,value in df.items() if not callable(value)}

            self._set_params(df_noncall)

            df_call={key:value for key,value in df.items() if callable(value)}

            for key,fun in df_call.items():

                if fun.__code__.co_argcount==0:

                    df_call[key]=fun()

                elif fun.__code__.co_argcount==1:

                    df_call[key]=fun(self)

            self._set_params(df_call)

            if self.get_params()==pre_params:

                stable=True

    def export_all(self):
        ''' Exports all cell parameters.

        Returns
        ----------
        df : dict.

            Note: dict values can be function of self.

        '''

        df=self.get_params()

        if hasattr(self,'resistance_squares'):

            df["Resistance"]=self.resistance_squares

        modkeys=[*df.keys()]

        # pop_all_match(modkeys,".*Layer*")

        pop_all_dict(df,[item for item in [*df.keys()] if item not in modkeys])

        return df

    def export_summary(self):
        ''' Exports summary of cell parameters.

        Returns
        ----------
        df : dict.

            Note: dict values can be function of self.

        '''

        df=self.get_params()

        modkeys=[*df.keys()]

        pop_all_match(modkeys,".*Layer*")

        pop_all_match(modkeys,".*Resistance*")

        pop_all_match(modkeys,".*Capacitance*")

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

        df=Series(self.export_summary())

        return df.to_string()

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

def check(device : Device, joined=False, blocking=True):
    ''' Shows the device layout.

        If run by terminal, blocks script until window is closed.

        Parameters
        ----------
            device : phidl.Device

            joined : boolean (optional, default False)

                if true, returns a flattened/joined version of device

    '''
    set_quickplot_options(blocking=blocking)

    if joined:

        cell=Device()
        cell.absorb(cell<<device)
        cell.flatten()
        qp(join(cell))

    else:

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
        is passed to obj._set_params().
    '''

    from re import search

    for name,value in param.items():

        match=search(tag,name)

        if match and match.start()==0:

            varname=name.replace(tag,"")

            obj._set_params({varname:value})

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

def pirel_cache(fun):

    from functools import wraps

    @wraps(fun)

    def wrapper(self):

        cls=_get_class_that_defined_method(fun)

        params=_get_class_param(cls)

        pop_all_match(params,'.*name*')

        dict_name="_"+fun.__name__+"_lookup"

        paramhash=_get_hashable_params(self,params)

        if not hasattr(cls,dict_name):

            setattr(cls,dict_name,{})

        dict_lookup=getattr(cls,dict_name)

        if paramhash in dict_lookup.keys():

            # print(f"found {cls.__name__} cell")

            return dict_lookup[paramhash]

        else:

            # print(f"build {cls.__name__} cell")

            xout=fun(self)

            dict_lookup[paramhash]=xout

            return xout

    return wrapper

def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return str(msg) + '\n'

def _get_class_param(cls : LayoutPart.__class__ ) -> list:

    out_list=[]

    if hasattr(cls,'_params_dict'):

        for p in cls._params_dict.values():

                out_list.append(p.lstrip('_'))

    [out_list.append(x.lower()) for x in cls.get_components()]

    return out_list

def _get_class_that_defined_method(meth):
    #from stackoverflow

    if isinstance(meth, functools.partial):

        return get_class_that_defined_method(meth.func)

    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):

        for cls in inspect.getmro(meth.__self__.__class__):

            if meth.__name__ in cls.__dict__:

                return cls

        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing

    if inspect.isfunction(meth):

        cls = getattr(inspect.getmodule(meth),

                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],

                      None)

        if isinstance(cls, type):

            return cls

    return getattr(meth, '__objclass__', None)  # handle special descriptor objects

def _get_hashable_params( obj : LayoutPart , params : list) ->tuple:

    paramdict={}

    for name in params:

        value=getattr(obj,name)

        if isinstance(value, LayoutPart ):

            paramdict.update({name:_get_hashable_params(value,_get_class_param(value.__class__))})

        else:

            try:

                port_list=tuple([(p.name,Point(p.midpoint).coord,p.width,p.orientation) for p in value])

                paramdict.update({name:port_list})

            except Exception:

                paramdict.update({name:value})

    return tuple(paramdict.items())

def _check_points_path(*points,trace_width=100):

    for i,p in enumerate(points):

        if not isinstance(p,Point):

            raise ValueError("wrong input")

        if i==0:

            pass

        else:

            p_ref=points[i-1]

            dist=p-points[i-1]

            if abs(dist)<trace_width/10:

                p_new=p_ref+p*(trace_width/abs(p))

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

def generate_gds_from_image(path,**kwargs):

    import nazca as nd

    if isinstance(path,pathlib.Path):

        path=str(path.absolute())

    else:

        path=pathlib.Path(path)

    cell=nd.image(path,**kwargs).put()

    path=path.parent/(path.stem+".gds")

    nd.export_gds(filename=str(path.absolute()))

    return path

def import_gds(path,cellname=None,flatten=True,**kwargs):

    if isinstance(path,str):

        path=pathlib.Path(path)

    cell=pg.import_gds(str(path.absolute()))

    if flatten==True:
        cell.flatten()

    if cellname is not None:

        cell._internal_name=cellname

    return cell

def magic_matrix(cells,master,overlap=Point(0,0)):
    ''' Arranges N cells in a NxN matrix with staggered position.

    Used in wafer positioning to have N cells in the center of the wafer.

    Parameters
    ----------
        cells : list of phidl.Device

        master : phidl.Device

            container of the cell matrix

        overlap : pt.Point (default (0,0))

            overlapping of cells.
    '''

    from itertools import cycle

    import phidl.device_layout as dl

    g= dl.Group(cells)

    g.align(alignment='ymin')
    g.align(alignment='xmin')

    l=len(cells)

    indexes=cycle([*range(l)])

    pos_matrix=[]

    for k in range(l):

        pos_matrix.append([next(indexes) for i in range(l)])

        next(indexes)

        for x in range(k):

            next(indexes)

    for j in range(l):

        for i in range(l):

            c=cells[pos_matrix[j][i]]

            origin=Point(c.xmin,c.ymin)

            transl=Point((c.xsize+overlap.x)*i,-(c.ysize+overlap.y)*j)

            c_ref=master<<c

            c_ref.move(origin=origin.coord,\
                destination=(origin+transl).coord)

    return master

def image_to_gds(p : pathlib.Path ,
    layer :int = LayoutDefault.layerTop ,
    *a,**k ):

    try:

        import nazca as nd

    except Exception:

        import subprocess

        import sys

        thispath=pathlib.Path(__file__).parent

        nazcapath=thispath/"addOns"/"nazca"/"nazca-0.5.13.zip"

        subprocess.check_call([sys.executable, "-m", "pip", "install", str(nazcapath.absolute())])

        import nazca as nd

    nd.image(str(p.absolute()),layer=layer, **k).put(0)

    nd.export_gds(filename=str(p.parent/p.stem)+'.gds', flat=True)

def is_cell_within(
    cell_test : Device ,
    cell_ref : Device,
    tolerance: float =0):
    ''' Checks whether cell_test is contained in cell_ref.

    Parameters:
    ---------
    cell_test : Device

    cell_ref : Device

    tolerance : float (optional)

    Returns:
        True (if strictly cell_test<cell_ref)
        False (otherwise).

    Note:
        if tolerance is not zero, then function returns True if cell<cell_ref+-tolerance
        in all direction
    '''

    if tolerance==0:

        return _is_cell_within(cell_test,cell_ref)

    else:

        shifts_set=np.array([[1,1],[-1,-1],[1,-1],[-1,1]])*tolerance

        for shift in shifts_set:

            cell_test.move(destination=shift)

            if not _is_cell_within(
                cell_test,
                cell_ref):

                cell_test.move(destination=-shift)

                return False

            else:

                cell_test.move(destination=-shift)

        else:

            return True

def _is_cell_within(cell_test,cell_ref):

    area_pre,area_post=_calculate_pre_post_area(cell_test,cell_ref)

    if round(area_pre,3) >= round(area_post,3):

        return True

    else:

        return False

def is_cell_outside(
    cell_test : Device ,
    cell_ref : Device,
    tolerance: float =0):
    ''' Checks whether cell_test is not overlap with cell_ref.

    Parameters:
    ---------
    cell_test : Device

    cell_ref : Device

    tolerance : float (optional)

    Returns:
        True (if strictly cell_tot>=cell_test+cell_ref)
        False (otherwise).

    Note:
        if tolerance is not zero, then function returns True if cell_tot>=cell_test+cell_ref-tol
        in all direction
    '''

    if tolerance==0:

        return _is_cell_outside(cell_test,cell_ref)

    else:

        shifts_set=np.array([[1,1],[-1,-1],[1,-1],[-1,1]])*tolerance

        for shift in shifts_set:

            cell_test.move(destination=shift)

            if not _is_cell_outside(
                cell_test,
                cell_ref):

                cell_test.move(destination=-shift)

                return False

            else:

                cell_test.move(destination=-shift)

        else:

            return True

def _is_cell_outside(cell_test,cell_ref):

    area_test=cell_test.area()

    area_ref,area_post=_calculate_pre_post_area(cell_test,cell_ref)

    if round(area_post,3)>=round(area_ref+area_test,3):

        return True

    else:

        return False

def _calculate_pre_post_area(cell_test,cell_ref):

    area_pre=_get_cell_area(cell_ref)

    c_flat=pg.union(cell_ref, by_layer=False, layer=100)

    if isinstance(cell_test,Device):

        c_flat.add_ref(cell_test)

    else:

        if isinstance(cell_test,DeviceReference):

            c_flat.add(cell_test)

    area_post=_get_cell_area(c_flat)

    return area_pre,area_post

def _get_cell_area(cell):

    c_flat=pg.union(cell, by_layer=False, layer=100)

    return c_flat.area()

def _get_centroid(*points):

    x_c=0
    y_c=0

    for p in points:

        x_c=x_c+p.x
        y_c=y_c+p.y

    return Point(x_c,y_c)/length(p)

def pick_callable_param(pars : dict):

    out_pars={}

    for key,value in pars.items():

        if callable(value):

            out_pars.update({key:value})

    return out_pars

def _get_angle(p1,p2):

    if not (isinstance(p1,Point) and isinstance(p2,Point)):

        raise ValueError(f"{p1} and {p2} have to be pirel Points")

    import numpy as np

    ang1 = np.arctan2(p1.y,p1.x)

    ang2 = np.arctan2(p2.y,p2.x)

    return np.rad2deg((ang1 - ang2) % (2 * np.pi))

warnings.formatwarning = custom_formatwarning

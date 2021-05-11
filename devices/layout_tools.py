import numpy as np

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray

from phidl import set_quickplot_options

from phidl import quickplot as qp

class Point:
    ''' Handles 2-d coordinates.

    Arguments
    --------
    x : float
    y : float.
    '''

    def __init__(self,x=0,y=0):

        self.x=x

        self.y=y

    def get_coord(self):
        ''' returns coordinates in a 2-d tuple'''

        return (self.x,self.y)

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

    def __call__(self):

        return (self.x,self.y)

    __radd__ = __add__

    def from_iter(self,l):
        '''build a new Point from an iterable.

        Parameters
        ----------

        l : length 2 iterable of floats

        Returns
        -------
        p : sketch.Point
            a new point.
        '''

        if not len(l)==2:

            raise Exception("Point can be built from iterable of length 2 only")

        self.x=l[0]
        self.y=l[1]

        return self

    def __mul__(self,x0):

        if isinstance(x0,int) or isinstance(x0,float):

            x1=self.x*x0
            y1=self.y*x0

            return Point(x1,y1)

        else:

            raise Exception("Division Point/x0 is not possible here")

    __rmul__=__mul__

class LayoutDefault:
    '''container of PyResLayout constants.'''

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

    TextParams={'font':"BebasNeue-Regular.otf",'size':125,'location':'top',\
        'distance':Point(0,100),'label':"default",'layer':layerTop}

    #IDT

    IDT_y = 200
    IDTpitch = 8
    IDTcoverage = 0.7
    IDTy_offset = 10
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
    Anchoretch_margin=Point(4,4)
    Anchoretch_x=EtchPit_x
    Anchorx_offset=0
    Anchorlayer=IDTlayer
    Anchoretch_layer=EtchPitlayer
    Anchoretch_choice=True

    #LFERes
    LFEResactive_area_margin=0.5
    #FBERes

    FBEResplatelayer=layerBottom
    #GSProbe
    GSProbepitch = 150
    GSProbepad_size = Point(80,80)
    GSProberouting_width = 80
    GSProbelayer = layerTop
    GSProberouting = True
    GSProbespacing = Point(20,30)

    #Via

    Vialayer=layerVias
    Viashape='circle'
    Viasize=5

    #GSGProbe

    GSGProbelayer=layerTop
    GSGProbepitch=200
    GSGProbesize=Point(100,100)

    GSProbelayer=GSGProbelayer
    GSProbepitch=GSGProbepitch
    GSProbesize=GSGProbesize

    #TFERes

    TFEResbottomlayer=layerBottom

    #Routing

    Routingtrace_width=80
    Routingclearance=(Point(0,250)(),Point(300,550)())
    Routinglayer=layerTop
    Routingports=(Port(name='1',midpoint=(450,0),\
        width=50,orientation=90),\
            Port(name='2',midpoint=(100,550),\
            width=50,orientation=90))

    #DUT
    DUTrouting_width=Routingtrace_width
    DUTprobe_dut_distance=50

    #GSGProbe_LargePad
    GSGProbe_LargePadground_size=200

    #ParametricArray

    Arrayx_spacing=50
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

    Padsize=400
    Padlayer=IDTlayer
    Paddistance=200
    Padport=Port(name='top',midpoint=(50,50),width=100,\
        orientation=-90)

def add_compass(device):
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

def draw_array(cell,x,y,row_spacing=0,column_spacing=0):
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

    cell_size=Point().from_iter(cell.size)+Point(column_spacing,row_spacing)

    o,_,_,_=get_corners(new_cell)

    cellmat=[]

    ports=[]

    for j in range(y):

        cellvec=[]

        for i in range(x):

            cellvec.append(new_cell<<cell)

            cellvec[i].move(origin=o(),
                destination=(o+Point(cell_size.x*i,cell_size.y*j))())

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

def print_ports(device):
    ''' print a list of ports in the cell.

    Parameters
    ----------
    device : phidl.Device.
    '''

    for i,p in enumerate(device.get_ports()):

        print(i,p,'\n')

def join(device):
    ''' returns a copy of device with all polygons joined.

    Parameters
    ----------
    device : phidl.Device.
    '''
    out_cell=pg.union(device,by_layer=True, precision=0.001,join_first=False)

    return out_cell

def get_corners(device):
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

def check_cell(device):
    ''' Shows the device layout.

    Blocks script until window is closed.
    '''
    set_quickplot_options(blocking=True)
    qp(device)

def if_match_import(obj,param,tag):
    ''' used to load data in subclasses.

    Parameters
    ---------
    obj : LayoutPart
        a instance that might contain parameters in 'df'

    param : str

    tag : str

    df : pd.DataFrame

    Use:
        if_match_import() looks for 'tag' in 'param' string;
        if 'tag' is found at begignning of 'param',
        'tag' it is removed from 'param'.
        A copy of 'df' with 'param' key changed into the new string
         is passed to obj.import_params().
    '''
    from re import search

    for name,value in param.items():

        match=search(tag,name)

        if match and match.start()==0:

            varname=name.replace(tag,"")

            obj.import_params({varname:value})

def add_prefix_dict(old_dict,tag):

    new_dict={}

    for name in old_dict.keys():

        new_dict[tag+name]=old_dict[name]

    return new_dict

def pop_all_dict(old_dict,elems):

    for el in elems:

        old_dict.pop(el)

    return old_dict

def parallel_res(*args):

    sum_y=0

    for arg in args:

        sum_y=sum_y+1/arg

    return 1/sum_y

def _add_lookup_table(fun):

    def wrapper(self):

        totparamlist=self.export_params()

        paramlist={}

        dict_name="_"+fun.__name__+"_lookup"

        for name in totparamlist.keys():

            if not "Name" in name:

                paramlist[name]=totparamlist[name]

        paramlist=tuple(paramlist.items())

        if not hasattr(self,dict_name):

            setattr(self,dict_name,{})

        dict_lookup=getattr(self,dict_name)

        if paramlist in dict_lookup.keys():

            return dict_lookup[paramlist]

        else:

            xout=fun(self)

            dict_lookup[paramlist]=xout

            return xout

    return wrapper

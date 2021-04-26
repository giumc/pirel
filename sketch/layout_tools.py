import numpy as np

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray

from phidl import set_quickplot_options
from phidl import quickplot as qp

class LayoutDefault:
    '''container of PyResLayout constants.'''

    def __init__(self):

        self.origin=Point(0,0)
        self.layerSi = 0
        self.layerBottom = 1
        self.layerTop = 2
        self.layerPad = 3
        self.layerEtch = 4
        self.layerVias = 5
        self.layerPartialEtch = 6
        self.layerBackSide = 7
        self.layerMask = 99

        #text

        self.TextParams={'font':"BebasNeue-Regular.otf",'size':125,'location':'top',\
            'distance':Point(0,100),'label':"default",'layer':self.layerTop}

        #IDT

        self.IDT_y = 200
        self.IDTpitch = 8
        self.IDTcoverage = 0.7
        self.IDTy_offset = 10
        self.IDTlayer = self.layerTop
        self.IDTn = 40

        #Bus

        self.Bussize=Point(self.IDTpitch*2*self.IDTn,self.IDTpitch*2)
        self.distance=Point(0,self.IDT_y+self.IDTy_offset)

        #EtchPit

        self.EtchPit_x=self.Bussize.x/4
        self.EtchPitactive_area=Point(self.Bussize.x,self.IDT_y+self.IDTy_offset+2*self.Bussize.y)
        self.EtchPitlayer=self.layerEtch

        #Anchor
        self.Anchorsize=Point(self.IDTpitch*self.IDTn/4,2*self.Bussize.y)
        self.Anchoretch_margin=Point(4,4)
        self.Anchoretch_x=self.EtchPit_x
        self.Anchoretchx_offset=0
        self.Anchorlayer=self.IDTlayer
        self.Anchoretch_layer=self.EtchPitlayer
        self.Anchoretch_choice=True
        #FBERes
        self.FBEResplatelayer=self.layerBottom
        #GSProbe
        self.GSProbepitch = 150
        self.GSProbepad_size = Point(80,80)
        self.GSProberouting_width = 80
        self.GSProbelayer = self.layerTop
        self.GSProberouting = True
        self.GSProbespacing = Point(20,30)

        #Via

        self.Vialayer=self.layerVias
        self.Viatype='circle'
        self.Viasize=5

        #GSGProbe

        self.GSGProbelayer=self.layerTop
        self.GSGProbepitch=200
        self.GSGProbesize=Point(100,100)

        self.GSProbelayer=self.GSGProbelayer
        self.GSProbepitch=self.GSGProbepitch
        self.GSProbesize=self.GSGProbesize

        #TFERes

        self.TFEResbottomlayer=self.layerBottom

        #Routing

        self.Routingtrace_width=80
        self.Routingclearance=(Point(0,250)(),Point(300,550)())
        self.Routinglayer=self.layerTop
        self.Routingports=(Port(name='1',midpoint=(450,0),\
            width=50,orientation=90),\
                Port(name='2',midpoint=(100,550),\
                width=50,orientation=90))

        #DUT
        self.DUTrouting_width=self.Routingtrace_width
        self.DUTprobe_dut_distance=50

        #GSGProbe_LargePad
        self.GSGProbe_LargePadground_size=200

        #ParametricArray

        self.Arrayx_spacing=50
        self.Arrayx_param={"IDTPitch":[_ for _ in range(1,4)]}
        self.Arraylabels_top=["IDTP"+str(x) for x in self.Arrayx_param.values()]
        self.Arraylabels_bottom=[str(x) for x in self.Arrayx_param.values()]

        #ParametricMatrix
        self.Matrixy_param={"IDTLength":[_ for _ in range(100,400,100)]}
        self.Matrixy_spacing=self.Arrayx_spacing
        self.Matrixlabels_top=[ [x+y for x in self.Arrayx_param]\
            for y in ["L"+str(z) for z in self.Matrixy_param.values()]]
        self.Matrixlabels_bottom=[ [str(x)+str(y) for x in self.Arrayx_param.values()] \
            for y in self.Matrixy_param.values()]

        #Stack
        self.Stackn=4
        #Pad
        self.Padsize=400
        self.Padlayer=self.IDTlayer
        self.Paddistance=200
        self.Padport=Port(name='top',midpoint=(50,50),width=100,\
            orientation=-90)

class Point:
    ''' Handles 2-d coordinates.

    Arguments
    --------
    x : float
    y : float.
    '''

    def __init__(self,x=0,y=0):

        self.x=np.around(np.single(x),decimals=2)
        self.y=np.around(np.single(y),decimals=2)

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
        # return f"{self.x}"

    def __call__(self):

        return (self.x,self.y)

    __radd__ = __add__

    # __div__ = __floordiv__

    # __truediv = __floordiv__

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

    new_cell=pg.Device(name=cell.name+"array")

    cell_size=Point().from_iter(cell.size)

    o,_,_,_=get_corners(new_cell)

    cellmat=[[]]

    ports=[]

    for j in range(y):

        for i in range(x):

            cellmat[j].append(new_cell<<cell)

            cellmat[j][i].move(origin=o(),
                destination=(o+Point(cell_size.x*i,cell_size.y*j))())

            for p in cellmat[j][i].ports.values():

                ports.append(Port(name=p.name+str(i),\
                    midpoint=p.midpoint,\
                    width=p.width,\
                    orientation=p.orientation))

    new_cell=join(new_cell)

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
    return pg.union(device,by_layer=True, precision=0.1,join_first=False)

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

def if_match_import(obj,param,tag,df):
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

    match=search(tag,param)

    if match and match.start()==0:

        varname=param.replace(tag,"")
        # print(varname)
        obj.import_params(df.rename(columns={param:varname}))

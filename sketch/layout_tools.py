import numpy as np

import phidl.geometry as pg

from phidl.device_layout import Port

from phidl import set_quickplot_options
from phidl import quickplot as qp

class LayoutDefault:

    def __init__(self):

        self.origin= Point(0,0)
        self.layerSi = 0
        self.layerBottom = 1
        self.layerTop = 2
        self.layerPad = 3
        self.layerEtch = 4
        self.layerVias = 5
        self.layerPartialEtch = 6
        self.layerBackSide = 7
        self.layerMask = 99

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

        #GSGProbe_LargePad
        self.GSGProbe_LargePadground_size=200

        #ParametricArray

        self.Arrayx_spacing=50
        self.Arrayx_param={"IDTPitch":[_ for _ in range(1,4)]}
        self.Arraylabels_top=["P"+str(x) for x in self.Arrayx_param.values()]
        self.Arraylabels_bottom=[str(x) for x in self.Arrayx_param.values()]

        #ParametricMatrix
        self.Matrixy_param={"IDTLength":[_ for _ in range(100,400,100)]}
        self.Matrixy_spacing=self.Arrayx_spacing
        self.Matrixlabels_top=[ [x+y for x in self.Arrayx_param]\
            for y in ["L"+str(z) for z in self.Matrixy_param.values()]]
        self.Matrixlabels_bottom=[ [str(x)+str(y) for x in self.Arrayx_param.values()] \
            for y in self.Matrixy_param.values()]

class Point:

    def __init__(self,x=0,y=0):

        self.x=np.around(np.single(x),decimals=2)
        self.y=np.around(np.single(y),decimals=2)

    def get_coord(self):

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

    def __floordiv__(self,x0):

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

    def from_iter(self,l):

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

    bound_cell=pg.compass(size=device.size).move(\
    origin=(0,0),destination=device.center)

    ports=port=bound_cell.get_ports()

    device.add_port(port=ports[0],name=device.name+'N')
    device.add_port(port=ports[1],name=device.name+'S')
    device.add_port(port=ports[2],name=device.name+'E')
    device.add_port(port=ports[3],name=device.name+'W')

    # return device

def print_ports(device):

    for i,p in enumerate(device.get_ports()):

        print(i,p,'\n')

def join(device):

    return pg.union(device,by_layer=True, precision=0.1,join_first=False)

def get_corners(device):

    bbox=device.bbox
    ll=Point(bbox[0,0],bbox[0,1])
    lr=Point(bbox[1,0],bbox[0,1])
    ul=Point(bbox[0,0],bbox[1,1])
    ur=Point(bbox[1,0],bbox[1,1])

    return ll,lr,ul,ur

def check_cell(device):

    set_quickplot_options(blocking=True)
    qp(device)

def if_match_import(obj,col,tag,df):

    from re import search

    match=search(tag,col)

    if match and match.start()==0:

        varname=col.replace(tag,"")
        # print(varname)
        obj.import_params(df.rename(columns={col:varname}))

import numpy as np

import phidl.geometry as pg

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
        self.IDTn = 4

        #Bus

        self.Bussize=Point(self.IDTpitch*2*self.IDTn,self.IDTpitch*2)
        self.distance=Point(0,self.IDT_y+self.IDTy_offset)

        #EtchPit

        self.EtchPit_x=20
        self.EtchPitactive_area=Point(self.Bussize.x,self.IDT_y+self.IDTy_offset+2*self.Bussize.y)
        self.EtchPitlayer=self.layerEtch

        #Anchor
        self.Anchorsize=Point(self.IDTpitch*self.IDTn/4,2*self.Bussize.y)
        self.Anchoretch_margin=Point(4,4)
        self.Anchoretch_x=self.EtchPit_x
        self.Anchoretchx_offset=self.IDTpitch/2
        self.Anchorlayer=self.IDTlayer
        self.Anchoretch_layer=self.EtchPitlayer

        #FBERes
        self.FBEResplatelayer=self.layerBottom
        #GSProbe
        self.GSProbepitch = 150
        self.GSProbepad_size = Point(80,80)
        self.GSProberouting_width = 80
        self.GSProbelayer = self.layerTop
        # self.GSProbebottom_marker = Line(Point(20,100),Point(120,100))
        # self.GSProbetop_marker = Line(Point(20,220), Point(120,320))
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


class Point:

    def __init__(self,x=0,y=0):

        self.x=x
        self.y=y

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

        return f"Point : x={self.x} y ={self.y}"
        # return f"{self.x}"

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

    return pg.union(device,by_layer=True)

def get_corners(device):

    bbox=device.bbox
    ll=Point(bbox[0,0],bbox[0,1])
    lr=Point(bbox[1,0],bbox[0,1])
    ul=Point(bbox[0,0],bbox[1,1])
    ur=Point(bbox[1,0],bbox[1,1])

    return ll,lr,ul,ur

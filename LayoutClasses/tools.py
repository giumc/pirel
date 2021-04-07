import numpy as np

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
        self.IDTcoverage = 0.5
        self.IDTy_offset = 4
        self.IDTlayer = self.layerTop
        self.IDTn = 40

        #Bus

        self.Bussize=Point(self.IDTpitch*2*self.IDTn,self.IDTpitch*2)
        self.distance=Point(0,self.IDT_y+self.IDTy_offset)

        #EtchPit

        self.EtchPit_x=20
        self.EtchPitactive_area=Point(self.Bussize.x,self.IDT_y+self.IDTy_offset+2*self.Bussize.y)
        self.EtchPitanchor_etch=True
        self.EtchPitetch_margin=Point(1,1)
        # self.EtchPitanchor_size=Point(self.EtchPit_x+self.EtchPitetch_margin.x+\
        #     self.EtchPitactive_area.x/4,2*self.Bussize.y)
        self.EtchPitanchor_size=Point(self.EtchPitactive_area.x/2,40)

        #GSProbe
        self.GSProbepitch = 150
        self.GSProbepad_size = Point(80,80)
        self.GSProberouting_width = 80
        self.GSProbelayer = self.layerTop
        # self.GSProbebottom_marker = Line(Point(20,100),Point(120,100))
        # self.GSProbetop_marker = Line(Point(20,220), Point(120,320))
        self.GSProberouting = True
        self.GSProbespacing = Point(20,30)

class LayoutTool:

    def get_size(self,cell):

        bounds=cell.get_bounding_box()

        dx = bounds[1,0]-bounds[0,0]
        dy = bounds[1,1]-bounds[0,1]

        return Point(dx,dy)

class Point:

    def __init__(self,x,y):

        self.x=x;
        self.y=y;

    def get_coord(self):

        return (self.x,self.y)

    def __add__(self,p):

        if not isinstance(p,Point):

            error("cannote add Point to non Point")

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

            p=self.get_coord()
            x1=p.x/x0
            y1=p.y/x0

            return Point(x1,y1)
        else:

            raise Exception("Division Point/x0 is not possible here")

    def __repr__(self):

        return f"Point : x={self.x} y ={self.y}"
        # return f"{self.x}"

    __radd__ = __add__

import numpy as np
import gdspy

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
        self.GSProbebottom_marker = Line(Point(20,100),Point(120,100))
        self.GSProbetop_marker = Line(Point(20,220), Point(120,320))
        self.GSProberouting = True
        self.GSProbespacing = Point(20,30)

class LayoutTool:

    def get_size(self,cell):

        bounds=cell.get_bounding_box()

        dx = bounds[1,0]-bounds[0,0]
        dy = bounds[1,1]-bounds[0,1]

        return Point(dx,dy)

    def merge_cells(self,*args,name="merged"):

        cell_out=gdspy.Cell(name)

        for cell in args:

            ref_cell=gdspy.CellReference(cell)

            cell_out.add(ref_cell)

        cell_out.flatten()

        return cell_out

class Point:

    def __init__(self,x,y):

        self.x=x;
        self.y=y;

    def get_coord(self):

        return np.array([self.x,self.y])

    def __add__(self,x0):

        if not isinstance(x0,Point):

            error("cannote add Point to non Point")

        x=self.get_coord()
        y=x+x0.get_coord()

        return Point(y[0],y[1])

    def __sub__(self,x0):

        if not isinstance(x0,Point):

            raise Exception("cannote sub Point to non Point")

        x=self.get_coord()

        y=x-x0.get_coord()

        return Point(y[0], y[1])

    def __floordiv__(self,x0):

        if isinstance(x0,int) or isinstance(x0,float):

            pmid=self.get_coord()/x0

            return Point(pmid[0],pmid[1])
        else:

            raise Exception("Division Point/x0 is not possible here")

    def __repr__(self):

        return f"Point : x={self.x} y ={self.y}"
        # return f"{self.x}"

    __radd__ = __add__

class Line:

    def __init__(self,p1,p2):

        if not isinstance(p1,Point) or not isinstance(p2,Point):

            raise Exception("Line(p1,p2) needs two Points")

        self.p1 = p1
        self.p2 = p2

    def get_mid_point(self):
        midp=(self.p1+self.p2).get_coord()/2
        return Point(midp[0],midp[1])

    def move(self,dp):

        return Line(self.p1+dp,self.p2+dp)

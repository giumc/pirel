import numpy as np

class LayoutDefault:

    def __init__(self):
        self.origin= np.array([0,0])
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

        self.IDT_y = 20
        self.IDTpitch = 2
        self.IDTcoverage = 0.5
        self.IDTy_offset = 2
        self.IDTlayer = self.layerTop
        self.IDTn = 5

        #BUS

        self.Bus_x=self.IDTpitch*2*self.IDTn
        self.Bus_y=self.IDTpitch*2
        self.distance=np.array([0,self.IDT_y+self.IDTy_offset])

        #EtchPit

        self.EtchPitactive_area=np.array([self.Bus_x,self.IDT_y+self.IDTy_offset+2*self.Bus_y])
        self.EtchPit_x=5
        self.EtchPitanchor=True
        self.EtchPitanchor_x=8
        self.EtchPitanchor_y=10

class LayoutTool:

    def get_size(self,cell):

        bounds=cell.get_bounding_box()

        dx = bounds[1,0]-bounds[0,0]
        dy = bounds[1,1]-bounds[0,1]

        return np.array([dx,dy])

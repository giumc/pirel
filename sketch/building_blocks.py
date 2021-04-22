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

from pandas import DataFrame

from layout_tools import *

ld=LayoutDefault()

class LayoutPart(ABC) :

    def __init__(self,name='default',*args,**kwargs):

        ld=LayoutDefault()

        self.name=name

        self.origin=ld.origin

        self.cell=Device()

    def view(self,*args,**kwargs):
        set_quickplot_options(blocking=True)
        qp(self.draw(*args,**kwargs))
        return

    def view_gds(self,*args,**kwargs):
        lib=gdspy.GdsLibrary('test')
        lib.add(self.draw(*args,**kwargs))
        gdspy.LayoutViewer(lib)

    def add_text(self,text_location='top',text_size=25,\
        text_label='default',text_font='BebasNeue-Regular.otf',\
        text_layer=ld.layerTop,text_distance=Point(0,100)):

        package_directory = os.path.dirname(os.path.abspath(__file__))

        font=os.path.join(package_directory,text_font)

        cell=self.cell

        o=Point(0,0)

        ll,lr,ul,ur=get_corners(cell)

        text_cell=pg.text(size=text_size,text=text_label,font=font,layer=text_layer)

        text_size=Point().from_iter(text_cell.size)

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

        self.cell=cell

    def print_params_name(self):

        df=self.export_params()

        print("List of parameters for instance of {}\n".format(self.__class__.__name__))

        print(*df.columns.values,sep='\n')

    def get_params_name(self):

        df=self.export_params()

        return [str(_) for _ in df.columns ]

    def bbox_mod(self,bbox):

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

    @abstractmethod
    def draw(self,*args,**kwargs):
        pass

    @abstractmethod
    def export_params(self):

        return DataFrame({
        'Type':self.__class__.__name__},index=[self.name])

    @abstractmethod
    def import_params(self,df):

        if len(df.index)>1:

            raise Exception("Single Row DataFrame is used to load parameters")

        self.name=df.index.values[0]

    @staticmethod
    def _add_columns(d1,d2):

        for cols in d2.columns:

            d1[cols]=d2[cols].iat[0]

        return d1

    @staticmethod
    def draw_array(cell,x,y,row_spacing=0,column_spacing=0,*args,**kwargs):

        new_cell=Device(name=cell.name+"array")

        cell_size=Point().from_iter(cell.size)

        new_cell.add_array(cell,rows=y,columns=x,\
            spacing=(row_spacing+cell_size.x,column_spacing+cell_size.y))

        _,_,ul,ur=get_corners(new_cell)

        midpoint=ul/2+ur/2

        p=Port(name=new_cell.name,\
            orientation=90,\
            midpoint=midpoint(),\
            width=(ur.x-ul.x))

        new_cell=join(new_cell)

        new_cell.add_port(p)

        return new_cell

    def __repr__(self):

        df=self.export_params()

        df["Name"]=df.index.values[0]

        df=df.rename(index={df.index.values[0]:'Values'})

        df=df.rename_axis("Parameters",axis=1)

        return df.transpose().to_string()

class IDT(LayoutPart) :

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.y = ld.IDT_y

        self.pitch = ld.IDTpitch

        self.y_offset = ld.IDTy_offset

        self.coverage = ld.IDTcoverage

        self.layer = ld.IDTlayer

        self.n = ld.IDTn

    def draw(self):

        o=self.origin

        rect=pg.rectangle(size=(self.coverage*self.pitch,self.y),\
            layer=self.layer)

        rect.move(origin=(0,0),destination=o())

        unitcell=Device(name=self.name)

        r1=unitcell << rect
        unitcell.absorb(r1)
        r2 = unitcell << rect

        r2.move(origin=o(),\
        destination=(o+Point(self.pitch,self.y_offset))())

        unitcell.absorb(r2)

        cell=Device()

        cell.name=self.name

        cell.add_array(unitcell,columns=self.n,rows=1,\
            spacing=(self.pitch*2,0))

        cell.flatten()

        totx=self.pitch*(self.n*2-1)-self.pitch*(1-self.coverage)

        midx=totx/2

        finger_dist=Point(self.pitch*1,\
        self.y+self.y_offset)

        cell.add_port(Port(name=self.name,\
        midpoint=(o+\
        Point(midx,0))(),\
        width=totx,
        orientation=-90))

        del unitcell,rect

        self.cell=cell

        return cell

    def get_finger_size(self):

        dy=self.y

        dx=self.pitch*self.coverage

        return Point(dx,dy)

    @property
    def active_area(self):

        return Point(self.pitch*self.n*2,self.y+self.y_offset)

    def export_params(self):

        t=LayoutPart.export_params(self)
        t["Length"]=self.y
        t["Pitch"]=self.pitch
        t["Offset"]=self.y_offset
        t["Coverage"]=self.coverage
        t["N_fingers"]=self.n

        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for cols in df.columns:

            if cols=='Length':

                self.y=df[cols].iat[0]

            elif cols=='Pitch':

                self.pitch=df[cols].iat[0]

            elif cols=='Offset':

                self.y_offset=df[cols].iat[0]

            elif cols=='Coverage':

                self.coverage=df[cols].iat[0]

            elif cols=='N_fingers':

                self.n=df[cols].iat[0]

            elif cols=='Layer':

                self.layer=df[cols].iat[0]

class Bus(LayoutPart) :

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.size=ld.Bussize
        self.distance=ld.distance
        self.origin = ld.origin
        self.layer = ld.layerTop

    def draw(self):

        o=self.origin

        pad=pg.rectangle(size=self.size(),\
        layer=self.layer).move(origin=(0,0),\
        destination=o())

        cell=Device(name=self.name)

        r1=cell<<pad
        cell.absorb(r1)
        r2=cell <<pad

        r2.move(origin=o(),\
        destination=(o+self.distance)())

        cell.absorb(r2)

        cell.add_port(name=self.name,\
        midpoint=(o+Point(self.size.x/2,self.size.y))(),\
        width=self.size.x,\
        orientation=90)

        self.cell=cell

        del pad

        return cell

    def export_params(self):

        t=LayoutPart.export_params(self)
        t["Width"]=self.size.x
        t["Length"]=self.size.y
        t["DistanceX"]=self.distance.x
        t["DistanceY"]=self.distance.y
        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for cols in df.columns:

            if cols=='Width':

                self.size.x=df[cols].iat[0]

            if cols=='Length':

                self.size.y=df[cols].iat[0]

            elif cols=='DistanceX':

                self.distance.x=df[cols].iat[0]

            elif cols=='DistanceY':

                self.distance.y=df[cols].iat[0]

            elif cols=='Layer':

                self.layer=df[cols].iat[0]

class EtchPit(LayoutPart) :

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.active_area=ld.EtchPitactive_area

        self.origin=ld.origin

        self.x=ld.EtchPit_x

        self.layer=ld.EtchPitlayer

    def draw(self):

        o=self.origin

        b_main=Bus()

        b_main.origin=o

        b_main.layer=self.layer

        b_main.size=Point(self.x,self.active_area.y)

        b_main.distance=Point(self.active_area.x+self.x,0)

        main_etch=b_main.draw()

        etch=Device(name=self.name)

        etch.absorb(etch<<main_etch)

        port_up=Port(self.name+'up',\
        midpoint=(o+Point(self.x+self.active_area.x/2,self.active_area.y))(),\
        width=self.active_area.x,\
        orientation=90)

        port_down=Port(self.name+'down',\
        midpoint=(o+Point(self.x+self.active_area.x/2,0))(),\
        width=self.active_area.x,\
        orientation=-90)

        etch.add_port(port_up)
        etch.add_port(port_down)

        del main_etch

        self.cell=etch

        return etch

    def export_params(self):

        t=LayoutPart.export_params(self)
        t["ActiveArea"]=self.active_area
        t["Width"]=self.x

        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for cols in df.columns:

            if cols =='ActiveArea':

                self.active_area=df[cols].iat[0]

            elif cols =='Width':

                self.x=df[cols].iat[0]

            elif cols=='Layer':

                self.layer=df[cols].iat[0]

class Anchor(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.size=ld.Anchorsize
        self.etch_margin=ld.Anchoretch_margin
        self.etch_choice=ld.Anchoretch_choice
        self.etch_x=ld.Anchoretch_x
        self.x_offset=ld.Anchoretchx_offset
        self.layer=ld.Anchorlayer
        self.etch_layer=ld.Anchoretch_layer

    def draw(self):

        o=self.origin

        anchor=pg.rectangle(\
            size=self.size(),\
            layer=self.layer)

        etch_size_mid=Point(\
        (self.etch_x-2*self.etch_margin.x-self.size.x)/2,\
        self.size.y-2*self.etch_margin.y)

        offset=Point(self.x_offset,0)

        cell=Device(name=self.name)

        etch_sx=pg.rectangle(\
            size=(etch_size_mid-offset)(),\
            layer=self.etch_layer)

        etch_dx=pg.rectangle(\
            size=(etch_size_mid+offset)(),\
            layer=self.etch_layer)

        etch_sx_ref=(cell<<etch_sx).move(origin=(0,0),\
        destination=(o+Point(0,self.etch_margin.y))())

        anchor_transl=o+Point(etch_sx.size[0]+self.etch_margin.x,0)

        anchor_ref=(cell<<anchor).move(origin=(0,0),\
        destination=anchor_transl())

        etchdx_transl=anchor_transl+Point(anchor.size[0]+self.etch_margin.x,self.etch_margin.y)

        etch_dx_ref=(cell<<etch_dx).move(origin=(0,0),\
        destination=etchdx_transl())

        cell.add_port(name=self.name,\
        midpoint=(anchor_transl+Point(self.size.x/2,self.size.y))(),\
        width=self.size.x,\
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

    def export_params(self):

        t=LayoutPart.export_params(self)
        t["Width"]=self.size.x
        t["Length"]=self.size.y
        t["EtchMarginX"]=self.etch_margin.x
        t["EtchMarginY"]=self.etch_margin.y
        t["EtchChoice"]=self.etch_choice
        t["EtchWidth"]=self.etch_x
        t["Offset"]=self.x_offset

        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for cols in df.columns:

            if cols=='Width':

                self.size.x=df[cols].iat[0]

            if cols=='Length':

                self.size.y=df[cols].iat[0]

            elif cols=="EtchMarginX":

                self.etch_margin.x=df[cols].iat[0]

            elif cols=="EtchMarginY":

                self.etch_margin.y=df[cols].iat[0]

            elif cols == "EtchChoice":

                self.etch_choice=df[cols].iat[0]

            elif cols == "Offset":

                self.x_offset=df[cols].iat[0]

            elif cols =='Layer':

                self.layer=df[cols].iat[0]

class Via(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=ld.Vialayer
        self.__type=ld.Viatype
        self.size=ld.Viasize

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self,string):

            if not (string=='circle' or string=='rectangle'):

                raise Exception("Vias can be only 'circle' or 'rectangle' for now")

            else:

                self.__type=string

    def draw(self):

        if self.type=='rectangle':

            if isinstance(self.size,Point):

                cell=pg.rectangle(size=self.size(),\
                    layer=self.layer)
            else:

                try:

                    cell=pg.rectangle(size=(self.size,self.size),\
                        layer=self.layer)

                except Exception:

                    raise Exception("Via.size has to be Point or int/float")

        elif self.type=='circle':

            if isinstance(self.size,Point):

                cell=pg.circle(radius=self.size.x/2,\
                layer=self.layer)

            else:

                try:

                    cell=pg.circle(radius=self.size/2,\
                    layer=self.layer)

                except Exception:

                    raise Exception("Via.size has to be Point or int/float")

        else:

            raise Exception("Something went wrong,abort")

        cell.move(origin=(0,0),\
            destination=self.origin())

        cell.name=self.name

        cell.add_port(Port(name=self.name,\
        midpoint=cell.center,\
        width=cell.xmax-cell.xmin,\
        orientation=90))

        self.cell=cell

        return cell

    def export_params(self):

        t=LayoutPart.export_params(self)
        t["Shape"]=self.type
        t["Size"]=self.size

        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for cols in df.columns:

            if cols=='Size':

                self.size=df[cols].iat[0]

            if cols=='Shape':

                self.shape=df[cols].iat[0]

            elif cols =='Layer':

                self.layer=df[cols].iat[0]

class Routing(LayoutPart):

    def __init__(self,side='auto',*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.layer=ld.Routinglayer
        self.trace_width=ld.Routingtrace_width
        self.clearance=ld.Routingclearance
        self.ports=ld.Routingports
        self.side=side

    def draw_frame(self):

        rect=pg.bbox(self.clearance,layer=self.layer)
        rect.add_port(self.ports[0])
        rect.add_port(self.ports[1])
        rect.name=self.name+"frame"

        return rect

    def draw(self):

        cell=Device(name=self.name)

        bbox=pg.bbox(self.clearance)

        ll,_,_,ur=get_corners(bbox)

        source=self.ports[0]

        destination=self.ports[1]

        if source.y>destination.y:

            source=self.ports[1]
            destination=self.ports[0]

        y_overtravel=ll.y-source.midpoint[1]-self.trace_width

        taper_len=min([max(y_overtravel,-self.trace_width/4),self.trace_width/4])

        if destination.y<=ll.y : # destination is below clearance

            if not(destination.orientation==source.orientation+180 or \
                destination.orientation==source.orientation-180):

                    raise Exception("Routing error: non-hindered routing needs +90 -> -90 oriented ports")

            source=self._add_taper(cell,source,len=taper_len)
            destination=self._add_taper(cell,destination,len=self.trace_width/4)

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

            if not(destination.orientation==source.orientation):

                raise Exception("Routing error: non-hindered routing needs +90 -> -90 oriented ports")

            ll,lr,ul,ur=get_corners(bbox)

            if source.x+self.trace_width/2>ll.x and source.x-self.trace_width/2<lr.x: #source tucked inside clearance

                if self.side=='auto':

                    source=self._add_taper(cell,source,len=taper_len)
                    destination=self._add_taper(cell,destination,len=self.trace_width/4)

                elif self.side=='left':

                    source=self._add_ramp_lx(cell,source,len=taper_len)
                    destination=self._add_taper(cell,destination,len=self.trace_width/4)

                elif self.side=='right':

                    source=self._add_ramp_rx(cell,source,len=taper_len)
                    destination=self._add_taper(cell,destination,len=self.trace_width/4)

                source.name='source'
                destination.name='destination'

                p0=Point().from_iter(source.midpoint)

                center_box=Point().from_iter(bbox.center)

                #left path
                p1=p0+Point(0,y_overtravel)
                p2=ll-Point(self.trace_width,self.trace_width)
                p3=p2+Point(0,1.5*self.trace_width+bbox.ysize)
                p4=Point(destination.x,p3.y)
                p5=Point(destination.x,destination.y)

                list_points_lx=[p0(),p1(),p2(),p3(),p4(),p5()]

                path_lx=pp.smooth(points=list_points_lx)
                #right path
                p1=p0+Point(0,y_overtravel)
                p2=lr+Point(self.trace_width,-self.trace_width)
                p3=p2+Point(0,1.5*self.trace_width+bbox.ysize)
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
                p1=Point(p0.x,ul.y+self.trace_width)
                p2=Point(destination.x,p1.y)
                p3=Point(destination.x,destination.y)

                list_points=[p0(),p1(),p2(),p3()]

                path=pp.smooth(points=list_points)#source tucked inside clearance

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

    def export_params(self):

        t=LayoutPart.export_params(self)
        t["TraceWidth"]=self.trace_width
        t["Clearance"]=self.clearance
        t["Ports"]=self.ports
        t["Side"]=self.side

        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for cols in df.columns:

            if cols=='TraceWidth':

                self.trace_width=df[cols].iat[0]

            elif cols=='Clearance':

                self.clearance=df[cols].iat[0]

            elif cols=='Ports':

                self.ports=df[cols].iat[0]

            elif cols=='Side':

                self.side=df[cols].iat[0]

            elif cols =='Layer':

                self.layer=df[cols].iat[0]

class GSProbe(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=ld.GSProbelayer
        self.pitch=ld.GSProbepitch
        self.size=ld.GSProbesize

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

        cell=Device(name=self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell
        pad_sig.move(origin=o(),\
        destination=(o+dp)())

        cell.add_port(Port(name=self.name+'_rx',\
        midpoint=(o+Point(pad_x/2+self.pitch,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name=self.name+'_lx',\
        midpoint=(o+Point(pad_x/2,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        self.cell=cell

        return cell

    def export_params(self):

        t=LayoutPart.export_params(self)
        t["Width"]=self.size.x
        t["Length"]=self.size.y
        t["Pitch"]=self.pitch

        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for cols in df.columns:

            if cols=='Width':

                self.size.x=df[cols].iat[0]

            elif cols=='Length':

                self.size.y=df[cols].iat[0]

            elif cols =='Pitch':

                self.pitch=df[cols].iat[0]

            elif cols =='Layer':

                self.layer=df[cols].iat[0]

class GSGProbe(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=ld.GSGProbelayer
        self.pitch=ld.GSGProbepitch
        self.size=ld.GSGProbesize

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

        cell=Device(name=self.name)

        dp=Point(self.pitch,0)
        pad_gnd_sx=cell<<pad_cell
        pad_sig=cell<<pad_cell
        pad_sig.move(origin=o(),\
        destination=(o+dp)())

        pad_gnd_dx=cell<<pad_cell
        pad_gnd_dx.move(origin=o(),\
        destination=(o+dp*2)())

        cell.add_port(Port(name=self.name+'_c',\
        midpoint=(o+Point(pad_x/2+self.pitch,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name=self.name+'_lx',\
        midpoint=(o+Point(pad_x/2,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        cell.add_port(Port(name=self.name+'_rx',\
        midpoint=(o+Point(pad_x/2+2*self.pitch,self.size.y))(),\
        width=pad_x,\
        orientation=90))

        self.cell=cell

        return cell

    def export_params(self):

        t=LayoutPart.export_params(self)
        t["Width"]=self.size.x
        t["Length"]=self.size.y
        t["Pitch"]=self.pitch

        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for cols in df.columns:

            if cols=='Width':

                self.size.x=df[cols].iat[0]

            elif cols=='Length':

                self.size.y=df[cols].iat[0]

            elif cols =='Pitch':

                self.pitch=df[cols].iat[0]

            elif cols =='Layer':

                self.layer=df[cols].iat[0]

class GSGProbe_LargePad(GSGProbe):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.groundsize=ld.GSGProbe_LargePadground_size

    def draw(self):

        cell=GSGProbe.draw(self)

        groundpad_new=pg.rectangle(size=(self.groundsize,self.groundsize),\
        layer=self.layer)

        groundpad_lx=cell<<groundpad_new

        port_lx=cell.get_ports()[1]

        groundpad_lx.move(origin=groundpad_new.bbox[1],\
        destination=(Point().from_iter(port_lx.midpoint)+Point(port_lx.width/2,0))())

        groundpad_rx=cell<<groundpad_new

        port_rx=cell.get_ports()[2]

        _,_,ur,_=get_corners(groundpad_new)
        groundpad_rx.move(origin=ur(),\
        destination=(Point().from_iter(port_rx.midpoint)-Point(port_rx.width/2,0))())

        port_c=cell.get_ports()[0]

        cell.absorb(groundpad_lx)
        cell.absorb(groundpad_rx)

        cell=join(cell)
        cell.add_port(port=port_c)
        cell.add_port(port=port_lx)
        cell.add_port(port=port_rx)

        self.cell=cell

        return cell

    def export_params(self):

        t=GSGProbe.export_params(self)

        t["GroundPadSize"]=self.groundsize

        return t

    def import_params(self,df):

        GSGProbe.import_params(self,df)

        for cols in df.columns:

            if cols=='GroundPadSize':

                self.groundsize=df[cols].iat[0]

class Pad(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.size=ld.Padsize
        self.layer=ld.Padlayer
        self.distance=ld.Paddistance
        self.port=ld.Padport

    def draw(self,*args,**kwargs):

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

    def export_params(self):

        t=super().export_params()

        t["Size"]=self.size
        t["Distance"]=self.distance

        return t

    def import_params(self,df):

        super().import_params(df)

        for cols in df.columns:

            if cols=='Size':

                self.size=df[cols].iat[0]

            if cols=='Distance':

                self.distance=df[cols].iat[0]

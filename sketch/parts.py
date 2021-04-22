from building_blocks import *

from layout_tools import *

ld=LayoutDefault()

import pandas as pd

import warnings

def Scaled(res):

    class Scaled(res):

        def __init__(self,*args,**kwargs):

            # self._valid_classes=(LFERes,FBERes,TFERes)
            #
            # if not any([res.__name__==x.__name__ for x in self._valid_classes]):
            #
            #     raise ValueError("Wrong init of scaled design. You can scale {}".format(",".join(self._valid_classes)))

            res.__init__(self,*args,**kwargs)

        def draw(self,*args,**kwargs):

            selfcopy=deepcopy(self)

            p=selfcopy.idt.pitch

            selfcopy.idt.y_offset=self.idt.y_offset*p

            selfcopy.idt.y=self.idt.y*p

            selfcopy.bus.size.y=self.bus.size.y*p

            selfcopy.etchpit.x=self.etchpit.x*selfcopy.idt.active_area.x

            selfcopy.anchor.size.x=self.anchor.size.x*selfcopy.idt.active_area.x

            selfcopy.anchor.size.y=self.anchor.size.y*p

            selfcopy.anchor.etch_margin.x=self.anchor.etch_margin.x*p

            selfcopy.anchor.etch_margin.y=self.anchor.etch_margin.y*p

            cell=res.draw(selfcopy,*args,**kwargs)

            del selfcopy

            self.cell=cell

            return cell

    return Scaled

def addVia(res,side='top',bottom_conn=False):

    if isinstance(side,str):

        side=[side]

    side=[(_).lower() for _ in side]

    class addVia(res):

        def __init__(self,*args,**kwargs):

            res.__init__(self,*args,**kwargs)
            self.via=Via(name=self.name+'Via')
            self.padlayers=[ld.layerTop,ld.layerBottom]
            self.overvia=2
            self.viadistance=100

        def draw(self,*args,**kwargs):

            # import pdb; pdb.set_trace()

            rescell=res.draw(self)

            active_width=rescell.xsize

            import numpy as np

            nvias=max(1,int(np.floor(active_width/3/self.via.size/self.overvia)))

            viacell=LayoutPart.draw_array(self._draw_padded_via(),nvias,3,*args,**kwargs)

            cell=Device(name=self.name)

            cell<<rescell

            pad=pg.compass(size=(viacell.xsize,self.viadistance),layer=self.padlayers[0])

            try:

                top_port=rescell.ports['top']

            except Exception:

                top_port=None

            try:

                bottom_port=rescell.ports['bottom']

            except Exception:

                bottom_port=None

            for sides in side:

                if sides=='top':

                    try :

                        rescell.ports['top']

                    except Exception:

                        raise ValueError ("Cannot add a top via in a cell with no top port")

                    top_port=self._attach_instance(cell, pad, pad.ports['S'], viacell, rescell.ports['top'])

                if sides=='bottom':

                    try :

                        rescell.ports['bottom']

                    except Exception:

                        raise ValueError ("Cannot add a bottom via in a cell with no bottom port")

                    bottom_port=self._attach_instance(cell, pad, pad.ports['N'], viacell, rescell.ports['bottom'])

            cell=join(cell)

            if top_port is not None:

                cell.add_port(top_port)

            if bottom_port is not None:

                cell.add_port(bottom_port)

            if bottom_conn==False:

                cell.remove_layers(layers=[self.padlayers[1]])

            self.cell=cell

            return cell

        def export_params(self):

            t=res.export_params(self)

            t_via=self.via.export_params().drop(columns=['Type'])

            t_via=t_via.rename(columns=lambda x: "Via"+x)

            t_via['Overvia']=self.overvia
            t_via['ViaDistance']=self.viadistance

            t=LayoutPart._add_columns(t,t_via)

            return t

        def import_params(self, df):

            res.import_params(self, df)

            for col in df.columns:

                if_match_import(self.via,col,"Via",df)

                if col=='Overvia':

                    self.overvia=df[col].iat[0]

                if col=='ViaDistance':

                    self.viadistance=df[col].iat[0]

        def bbox_mod(self,bbox):

            LayoutPart.bbox_mod(self,bbox)

            ll=Point().from_iter(bbox[0])
            ur=Point().from_iter(bbox[1])

            if any([_=='top' for _ in side]):

                ur=ur-Point(0,float(self.via.size*self.overvia*3*1.5))

            if any([_=='bottom' for _ in side]):

                ll=ll+Point(0,float(self.via.size*self.overvia*3*1.5))

            return (ll(),ur())

        def _draw_padded_via(self):

            viacell=self.via.draw()

            size=float(self.via.size*self.overvia)

            port=viacell.get_ports()[0]

            trace=pg.rectangle(size=(size,size),layer=self.padlayers[0])

            trace.move(origin=trace.center.tolist(),\
                destination=viacell.center.tolist())

            trace2=pg.copy_layer(trace,layer=self.padlayers[0],new_layer=self.padlayers[1])

            cell=Device(name=self.name)

            cell.absorb((cell<<trace))

            cell.absorb((cell<<trace2))

            cell.absorb(cell<<viacell)

            port.midpoint=(port.midpoint[0],cell.ymax)

            port.width=size

            cell=join(cell)

            cell.add_port(port)

            return cell

        def _attach_instance(self,cell,padcell,padport,viacell,port):

            # import pdb; pdb.set_trace()

            padref=cell<<padcell

            padref.connect(padport,\
                    destination=port)

            cell.absorb(padref)

            viaref=cell<<viacell

            viaref.connect(viacell.get_ports()[0],\
            destination=port,\
            overlap=-self.viadistance)

            port=Port(name=port.name,\
                midpoint=(port.midpoint[0],port.midpoint[1]),\
                width=viacell.xsize,\
                orientation=port.orientation)

            return port

    return addVia

def addPad(res):

    class addPad(res):

        def __init__(self,*args,**kwargs):

            res.__init__(self,*args,**kwargs)
            self.pad=Pad(name=self.name+'Pad')

        def draw(self,*args,**kwargs):

            destcell=res.draw(self,*args,**kwargs)

            for port in destcell.get_ports():

                self.pad.port=port

                ref=destcell<<self.pad.draw(*args,**kwargs)

                ref.connect(ref.ports['conn'],\
                    destination=port)

                destcell.absorb(ref)

            self.cell=destcell

            return destcell

        def export_params(self):

            t_pad=self.pad.export_params().drop(columns=['Type'])

            t_pad=t_pad.rename(columns=lambda x: "Pad"+x)

            t=res.export_params(self)

            t=LayoutPart._add_columns(t,t_pad)

            return t

        def import_params(self, df):

            res.import_params(self,df)

            for col in df.columns:

                if_match_import(self.pad,col,"Pad",df)

    return addPad

def addProbe(res,probe):

    class addProbe(res):

        def __init__(self,*args,**kwargs):

            res.__init__(self,*args,**kwargs)
            self.probe=probe
            
            elf.routing_width=ld.DUTrouting_width
            self.probe_dut_distance=ld.DUTprobe_dut_distance

        def draw(self,*a,**k):

            # import pdb; pdb.set_trace()

            device_cell=res.draw(self,*a,**k)

            probe_cell=self.probe.draw()

            cell=Device(name=self.name)

            probe_dut_distance=Point(0,self.probe_dut_distance)

            cell<<device_cell

            bbox=cell.bbox

            probe_ref=cell<<probe_cell

            ports=cell.get_ports()

            probe_ref.connect(ports[2],\
            destination=ports[1],overlap=-probe_dut_distance.y)

            ports=cell.get_ports()

            dut_port_bottom=ports[1]
            dut_port_top=ports[0]

            bbox=self.dut.bbox_mod(bbox)

            if isinstance(self.probe,GSGProbe):

                probe_port_lx=ports[3]
                probe_port_center=ports[2]
                probe_port_rx=ports[4]

                routing_lx=self._route(bbox,probe_port_lx,dut_port_top,side='left')

                routing_c=pg.taper(length=probe_dut_distance.y,\
                width1=probe_port_center.width,\
                width2=dut_port_bottom.width,layer=self.probe.layer)

                routing_rx=self._route(bbox,probe_port_rx,dut_port_top,side='right')
                routing_tot=pg.boolean(routing_lx,routing_rx,'or',layer=probe.layer)

                cell<<routing_tot
                center_routing=cell<<routing_c

                center_routing.connect(center_routing.ports[2],destination=dut_port_bottom)

            elif isinstance(self.probe,GSProbe):

                raise ValueError("DUT with GSprobe to be implemented ")

            else:

                raise ValueError("DUT without GSG/GSprobe to be implemented ")

            del probe_cell,device_cell,routing_lx,routing_rx,routing_c,routing_tot

            cell.flatten()

            cell=join(cell)

            self.cell=cell

            return cell

        def _route(self,bbox,p1,p2,*args,**kwargs):

            routing=Routing(*args,**kwargs)
            routing.layer=self.probe.layer
            routing.clearance=bbox
            routing.trace_width=self.routing_width
            routing.ports=(p1,p2)
            cell=routing.draw()
            del routing
            return cell
            # return routing.draw_frame()

        def export_params(self):

            t=super().export_params()

            t=t.rename(columns={"Type":"DUT_Type"})

            t=self._add_columns(t, t_dut)

            t_probe=self.probe.export_params()

            t_probe=t_probe.rename(columns=lambda x : "Probe"+x )

            t=self._add_columns(t,t_probe)

            t["RoutingWidth"]=self.routing_width

            t["ProbeDistance"]=self.probe_dut_distance

            t.index=[self.name]

            t=t.reindex(columns=["Type"]+[cols for cols in t.columns if not cols=="Type"])

            return t

        def import_params(self,df):

            self.dut.import_params(df)

            for col in df.columns:

                if_match_import(self.probe,col,"Probe",df)

                if col == "RoutingWidth" :
                    # import pdb; pdb.set_trace()
                    self.routing_width=df[col].iat[0]

                if col == "ProbeDistance" :

                    self.probe_dut_distance=df[col].iat[0]

    return addProbe

class LFERes(LayoutPart):

    def __init__(self,*args,**kwargs):

        LayoutPart.__init__(self,*args,**kwargs)

        self.layer=ld.IDTlayer

        self.idt=IDT(name=self.name+'IDT')

        self.bus=Bus(name=self.name+'Bus')

        self.etchpit=EtchPit(name=self.name+'EtchPit')

        self.anchor=Anchor(name=self.name+'Anchor')

    def draw(self):

        o=self.origin

        self.idt.origin=o

        self.idt.layer=self.layer

        idt_cell=self.idt.draw()

        cell=Device(name=self.name)

        idt_ref=cell<<idt_cell

        self.bus.size=Point(\
            2*self.idt.pitch*(self.idt.n-1)+(self.idt.coverage)*self.idt.pitch,\
            self.bus.size.y)

        self.bus.distance=Point(\
            self.idt.pitch,self.bus.size.y+self.idt.y+self.idt.y_offset)

        self.bus.layer=self.layer

        bus_cell = self.bus.draw()

        bus_ref= cell<<bus_cell

        ports=cell.get_ports()

        bus_ref.connect(port=ports[1],\
        destination=ports[0])

        cell.absorb(idt_ref)

        self.etchpit.active_area=Point().from_iter(cell.size)+\
        Point(self.idt.pitch*(1-self.idt.coverage),self.anchor.etch_margin.y*2)

        etch_cell=self.etchpit.draw()

        etch_ref=cell<<etch_cell

        ports=cell.get_ports()
        etch_ref.connect(ports[2],\
        destination=ports[0])

        etch_ref.move(origin=etch_ref.center,\
        destination=(Point().from_iter(etch_ref.center)+\
            Point(self.idt.pitch/2,-self.bus.size.y-self.anchor.etch_margin.y))())

        cell.absorb(bus_ref)

        # return cell

        self.anchor.etch_x=self.etchpit.x*2+self.etchpit.active_area.x

        self.anchor.layer=self.layer

        if self.anchor.size.x>self.bus.size.x:

            self.anchor.size=Point(self.bus.size.x,self.anchor.size.y)
            warnings.warn("Anchor is too wide, reduced to Bus width size")

        anchor_cell=self.anchor.draw()

        anchor_bottom=cell<<anchor_cell

        ports=cell.get_ports()

        anchor_bottom.connect(ports[2],
        destination=ports[1],overlap=self.anchor.etch_margin.y)
        anchor_bottom.move(origin=(0,0),\
        destination=(-self.anchor.x_offset,0))

        anchor_top=(cell<<anchor_cell)
        anchor_top.move(origin=anchor_top.center,\
        destination=anchor_bottom.center)
        anchor_pivot=ports[2]

        anchor_top.rotate(angle=180,center=ports[1].center)
        anchor_top.move(origin=(0,0),\
        destination=(0,self.etchpit.active_area.y))

        cell.absorb(etch_ref)

        ports=cell.get_ports()
        ports[0].rotate(180,center=ports[0].center)
        ports[1].rotate(180,center=ports[1].center)

        cell.absorb(anchor_top)
        cell.absorb(anchor_bottom)

        cell_out=join(cell)

        cell_out.add_port(Port(name="top",\
        midpoint=(Point().from_iter(ports[1].center)+\
        Point(0,self.anchor.size.y))(),\
        width=self.anchor.size.x,\
        orientation=90))

        cell_out.add_port(Port(name="bottom",\
        midpoint=(Point().from_iter(ports[0].center)-\
        Point(0,self.anchor.size.y))(),\
        width=self.anchor.size.x,\
        orientation=-90))

        del idt_cell,bus_cell,etch_cell,anchor_cell

        self.cell=cell_out

        return cell_out

    def export_params(self):

        t=super().export_params()

        t_res=self.idt.export_params().drop(columns=['Type'])

        t_res=t_res.rename(columns=lambda x: "IDT"+x)

        t=self._add_columns(t,t_res)

        t_bus=self.bus.export_params().drop(columns=['Type','DistanceX','DistanceY','Width'])
        t_bus=t_bus.rename(columns=lambda x: "Bus"+x)

        t=self._add_columns(t,t_bus)

        t_etch=self.etchpit.export_params().drop(columns=['Type','ActiveArea'])
        t_etch=t_etch.rename(columns=lambda x: "Etch"+x)

        t=self._add_columns(t,t_etch)

        t_anchor=self.anchor.export_params().drop(columns=['Type','EtchWidth','Offset','EtchChoice'])
        t_anchor=t_anchor.rename(columns=lambda x: "Anchor"+x)

        t=self._add_columns(t,t_anchor)

        t.index=[self.name]

        t=t.reindex(columns=['Type']+[col for col in t.columns if not col=='Type'])

        return t

    def import_params(self,df):

        LayoutPart.import_params(self,df)

        for col in df.columns:

            if_match_import(self.idt,col,"IDT",df)
            if_match_import(self.bus,col,"Bus",df)
            if_match_import(self.etchpit,col,"Etch",df)
            if_match_import(self.anchor,col,"Anchor",df)

class FBERes(LFERes):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.platelayer=ld.FBEResplatelayer

    def draw(self):

        cell=LFERes.draw(self)

        plate=pg.rectangle(size=self.etchpit.active_area(),\
        layer=self.platelayer)

        plate_ref=cell<<plate

        transl_rel=Point(self.etchpit.x,self.anchor.size.y-self.anchor.etch_margin.y)
        lr_cell=get_corners(cell)[0]
        lr_plate=get_corners(plate_ref)[0]
        plate_ref.move(origin=lr_plate(),\
        destination=(lr_plate+lr_cell+transl_rel)())

        cell.absorb(plate_ref)

        del plate

        self.cell=cell

        return cell

class TFERes(LFERes):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.bottomlayer=ld.TFEResbottomlayer

    def draw(self):

        cell=LFERes.draw(self)

        idt_bottom=copy(self.idt)
        idt_bottom.layer=self.bottomlayer

        idt_ref=cell<<idt_bottom.draw()

        idt_ref.mirror(p1=(idt_ref.xmin,idt_ref.ymin),\
        p2=(idt_ref.xmin,idt_ref.ymax))

        idt_ref.move(origin=(0,0),\
        destination=(idt_bottom.pitch*(idt_bottom.n*2-(1-idt_bottom.coverage)),0))

        cell.absorb(idt_ref)

        bus_bottom=copy(self.bus)
        bus_bottom.layer=self.bottomlayer

        bus_ref=cell<<bus_bottom.draw()

        bus_ref.mirror(p1=(bus_ref.xmin,bus_ref.ymin),\
         p2=(bus_ref.xmin,bus_ref.ymax))

        bus_ref.move(origin=(0,0),\
        destination=\
            (idt_bottom.pitch*(idt_bottom.n*2-(1-idt_bottom.coverage)),\
            -bus_bottom.size.y))

        cell.absorb(bus_ref)

        anchor_bottom=copy(self.anchor)

        anchor_bottom.layer=self.bottomlayer
        anchor_bottom.etch_choice=False

        anchor_ref=cell<<anchor_bottom.draw()
        anchor_ref.rotate(angle=180)

        ports=cell.get_ports()
        anchor_ref.connect(ports[2],ports[0])

        cell.absorb(anchor_ref)

        anchor_ref_2=cell<<anchor_bottom.cell
        anchor_ref_2.rotate(angle=180)
        ports=cell.get_ports()

        anchor_ref_2.connect(ports[2],ports[1])

        cell.absorb(anchor_ref_2)

        join(cell)

        # anchor_ref.move(origin=(0,0),\
        # destination=(50,0))

        del idt_bottom

        del bus_bottom

        del anchor_bottom

        self.cell=cell

        return cell

class Stack(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        try:

            if isinstance(args[0],LayoutPart):

                self.device=args[0]

        except Exception:

            self.device=LFERes(name=self.name+'Device')

        self.n=ld.Stackn

        self.gnd_width=self.device.pad.size*1.5

    @property

    def device(self):

        self._unpadded_device.import_params(self._padded_device.export_params())
        return self._padded_device

    @device.setter

    def device(self,dev):

        self._unpadded_device=dev

        device_with_pads=addPad(dev.__class__)()

        device_with_pads.import_params(dev.export_params())

        self._padded_device=device_with_pads

    def export_params(self):

        t=self.device.export_params()
        t["NCopies"]=self.n
        t["GndWidth"]=self.gnd_width

        return t

    def import_params(self,df):

        self.device.import_params(df)

        for cols in df.columns:

            if cols=='NCopies':

                self.n=df[cols].iat[0]

            if cols=='GndWidth':

                self.gnd_width=df[cols].iat[0]

    def draw(self,*args,**kwargs):

        device=self.device

        cell=LayoutPart.draw_array(device.draw(*args,**kwargs),\
            self.n,1)

        port=cell.get_ports()[0]

        cell=join(cell)

        out_port=Port(name='bottom',\
        midpoint=(port.midpoint[0],port.midpoint[1]-cell.ysize+device.pad.size),\
        width=cell.xsize,\
        orientation=-90)

        cell.add_port(out_port)

        gnd_width=self.gnd_width

        gndpad=pg.compass(size=(cell.xsize,gnd_width),layer=device.pad.layer)

        gnd_ref=cell<<gndpad

        gnd_ref.connect(gndpad.ports['N'],\
            destination=out_port)

        cell.absorb(gnd_ref)

        cell=join(cell)

        cell.add_port(out_port)

        self.cell=cell

        return cell

    def draw_with_test(self,*args,**kwargs):

        cell=self.draw(*args,**kwargs)

        dut=DUT(name=self.name+"Test")

        dut.dut=self._unpadded_device

        dut.probe=GSGProbe(name=dut.name+"Probe")

        dut.draw(*args,**kwargs)

        cell.add(dut.cell)

        dut.add_text(text_size=150,text_label=dut.name,text_location='left')

        g=Group([cell,dut.cell])

        g.distribute(direction='x',spacing=150)

        cell=join(cell)

        cell.name=dut.name

        return cell

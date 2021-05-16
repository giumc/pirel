from building_blocks import *

from layout_tools import *

from building_blocks import LayoutParamInterface

import pandas as pd

import warnings

from functools import cache

from itertools import chain

def Scaled(cls):

    ''' Class Decorator that accept normalized parameters for resonator designs.

    Descaling rules:
        IDT gap (d) = IDT gap (n) * pitch
        IDT length (d) = IDT length (n) * pitch
        Bus length (d) = Bus length (n) * pitch
        Etch pit width (d) = Etch pit width (d) * active region width
        Anchor width (d) = Anchor width (n) * active region width
        Anchor length (d) = Anchor length (n) * active region width
        Anchor Margin Y (d) = Anchor Margin Y (n) * Anchor length
        Anchor Margin X (d) = Anchor Margin X (n) * Anchor width.

    Parameters
    ----------
    cls : class

        pass class of resonator to be decorated.
        (i.e. Scaled(LFE)(name="normalized LFE")).
    '''

    class Scaled(cls):

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)
            self._normalized=False

        def import_params(self,df):

            self._normalize()

            cls.import_params(self,df)

            self._denormalize()

        def export_params(self):

            self._normalize()

            df=cls.export_params(self)

            self._denormalize()

            return df

        def _normalize(self):

            if self._normalized==True:

                raise ValueError("Already normalized")

            p=self.idt.pitch

            active_area_x=self.idt.active_area.x
            anchor_x=self.anchor.size.x
            anchor_y=self.anchor.size.y

            self.idt.y_offset=self.idt.y_offset/p

            self.idt.length=self.idt.length/p

            self.bus.size.y=self.bus.size.y/p

            self.etchpit.x=self.etchpit.x/active_area_x

            self.anchor.size.x=self.anchor.size.x/active_area_x

            self.anchor.size.y=self.anchor.size.y/p

            self.anchor.etch_margin.x=self.anchor.etch_margin.x/anchor_x

            self.anchor.etch_margin.y=self.anchor.etch_margin.y/anchor_y

            self._normalized=True

        def _denormalize(self):
            ''' Applies descaling rules and returns a copy of the descaled object.

            Descaling rules:
                IDT gap (d) = IDT gap (n) * pitch
                IDT length (d) = IDT length (n) * pitch
                Bus length (d) = Bus length (n) * pitch
                Etch pit width (d) = Etch pit width (d) * active region width
                Anchor width (d) = Anchor width (n) * active region width
                Anchor length (d) = Anchor length (n) * active region width
                Anchor Margin Y (d) = Anchor Margin Y (n) * Anchor length
                Anchor Margin X (d) = Anchor Margin X (n) * Anchor width.

            Returns
            -------
            selfcopy : object
                 a deep copy of the calling object, with descaled parameters.
            '''

            if self._normalized==False:

                raise ValueError("Already denormalized")

            p=self.idt.pitch

            self.idt.y_offset=self.idt.y_offset*p

            self.idt.length=self.idt.length*p

            self.bus.size.y=self.bus.size.y*p

            active_area_x=self.idt.active_area.x

            self.etchpit.x=self.etchpit.x*active_area_x

            self.anchor.size.x=self.anchor.size.x*active_area_x

            self.anchor.size.y=self.anchor.size.y*p

            self.anchor.etch_margin.x=self.anchor.etch_margin.x*self.anchor.size.x

            self.anchor.etch_margin.y=self.anchor.etch_margin.y*self.anchor.size.y

            self._normalized=False

            return self

    Scaled.__name__=" ".join(["Scaled",cls.__name__])

    return Scaled

def addVia(cls,side='top',bottom_conn=False):
    ''' Class decorator to add vias to resonators.

    you can select side (top,bottom or both) and if keep the bottom pad of the via.

    Parameters
    ----------
    cls : class
        the class that needs vias

    side : 'top','bottom', or iterable of both
        decides the port to attach vias to.

    bottom_conn : boolean
        as the vias are drawn by default with top-bottom pads, you can decide here to
        remove the second pad by default from all the designs.

    Attributes
    ----------

        via : PyResLayout.Via
            instance of a PyResLayout.Via class

        padlayers : lenght 2 iterable of int
            top/bottom layers to draw vias pads

        over_via : float
            ratio pad size / via size

        via_distance : float
            y distance between connecting port and via center

        via_area : PyResLayout.Point
            size (in coordinates) to be filled with vias.
    '''

    if isinstance(side,str):

        side=[side]

    side=[(_).lower() for _ in side]

    class addVia(cls):

        __components={"Via":Via}

        over_via=LayoutParamInterface()

        via_distance=LayoutParamInterface()

        via_area=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            for p,c in self.__components.items():

                setattr(self,p.lower(),c(name=self.name+p))

            self.padlayers=[LayoutDefault.layerTop,LayoutDefault.layerBottom]

            self.over_via=2

            self.via_distance=100

            self.via_area=Point(100,100)

        def draw(self):

            cell=Device()
            cell.name=self.name

            resdef=cell.add_ref(cls.draw(self))

            active_width=resdef.xsize

            nvias_x,nvias_y=self.get_n_vias()

            unit_cell=self._draw_padded_via()

            viacell=join(CellArray(unit_cell,\
                columns=nvias_x,rows=nvias_y,\
                spacing=(unit_cell.xsize,unit_cell.ysize))).flatten()

            viacell.add_port(Port(name='conn',\
                midpoint=(viacell.x,viacell.ymax),\
                width=viacell.xsize,\
                orientation=90))

            try:

                top_port=resdef.ports['top']

            except Exception:

                top_port=None

            try:

                bottom_port=resdef.ports['bottom']

            except Exception:

                bottom_port=None

            for sides in side:

                if sides=='top':

                    try :

                        top_port=resdef.ports['top']

                    except Exception:

                        raise ValueError ("Cannot add a top via in a cell with no top port")

                    pad=pg.compass(size=(top_port.width,self.via_distance),layer=self.padlayers[0])

                    top_port=self._attach_instance(cell, pad, pad.ports['S'], viacell, top_port)

                if sides=='bottom':

                    try :

                        bottom_port=resdef.ports['bottom']

                    except Exception:

                        raise ValueError ("Cannot add a bottom via in a cell with no bottom port")

                    pad=pg.compass(size=(bottom_port.width,self.via_distance),layer=self.padlayers[0])

                    bottom_port=self._attach_instance(cell, pad, pad.ports['N'], viacell, bottom_port)

            cell.flatten()

            for name,port in resdef.ports.items():

                cell.add_port(port,name)

            return cell

        def export_params(self):

            t=cls.export_params(self)

            t_via=self.via.export_params()

            t_via.pop('Name')

            t_via=add_prefix_dict(t_via,'Via')

            t.update(t_via)

            return t

        def import_params(self, df):

            cls.import_params(self,df)

            if_match_import(self.via,df,"Via")

        def _bbox_mod(self,bbox):

            LayoutPart._bbox_mod(self,bbox)

            ll=Point().from_iter(bbox[0])

            ur=Point().from_iter(bbox[1])

            nvias_x,nvias_y=self.get_n_vias()

            if any([_=='top' for _ in side]):

                ur=ur-Point(0,float(self.via.size*self.over_via*nvias_y+self.via_distance))

            if any([_=='bottom' for _ in side]):

                ll=ll+Point(0,float(self.via.size*self.over_via*nvias_y+self.via_distance))

            return (ll(),ur())

        def _draw_padded_via(self):

            viaref=DeviceReference(self.via.draw())

            size=float(self.via.size*self.over_via)

            port=viaref.ports['conn']

            trace=pg.rectangle(size=(size,size),layer=self.padlayers[0])

            trace.move(origin=trace.center,\
                destination=viaref.center)

            trace2=pg.copy_layer(trace,layer=self.padlayers[0],new_layer=self.padlayers[1])

            cell=Device(self.name)

            cell.absorb(cell<<trace)

            cell.absorb(cell<<trace2)

            cell.add(viaref)

            port.midpoint=(port.midpoint[0],cell.ymax)

            port.width=size

            cell.add_port(port)

            if bottom_conn==False:

                cell.remove_layers(layers=[self.padlayers[1]])

            return cell

        def _attach_instance(self,cell,padcell,padport,viacell,port):

            padref=cell<<padcell

            padref.connect(padport,\
                    destination=port)

            cell.absorb(padref)

            viaref=cell.add_ref(viacell,alias=self.name+'Via'+port.name)

            viaref.connect(viacell.ports["conn"],\
            destination=port,\
            overlap=-self.via_distance)

            return port

        def get_n_vias(self):

            import numpy as np

            nvias_x=max(1,int(np.floor(self.via_area.x/self.via.size/self.over_via)))
            nvias_y=max(1,int(np.floor(self.via_area.y/self.via.size/self.over_via)))

            return nvias_x,nvias_y

        @classmethod
        def get_class_param(self):

            param=LayoutPart.get_class_param(self)

            [param.append(x) for x in cls.get_class_param()]
            
            for p,c in self.__components.items():

                [param.append(p+x) for x in c.get_class_param()]

            return param

        def __getattr__(self,name):

            for p in self.__components.keys():

                if name.startswith(p):

                    return getattr(getattr(self,p.lower()),name.replace(p,''))

            else:

                raise AttributeError

    addVia.__name=" ".join([cls.__name__,"w Via"])

    return addVia

def addPad(cls):
    ''' Class decorator to add probing pads to existing cells.
        Parameters
        ----------
        cls : PyResLayout.LayoutPart
            design where pads have to be added

        Attributes
        ----------
        pad : PyResLayout.Pad
            pad design for the cell

        The pad design needs a port to attach to the existing cell,
            see help for more info.
        '''

    class addPad(cls):

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.pad=Pad(name=self.name+'Pad')

        def draw(self):

            cell=Device()

            cell.name=self.name

            d_ref=cell.add_ref(cls.draw(self))

            for name,port in d_ref.ports.items():

                self.pad.port=port

                pad_ref=cell.add_ref(self.pad.draw())

                pad_ref.connect(pad_ref.ports['conn'],\
                    destination=port)

                cell.absorb(pad_ref)

                cell.add_port(port,name)

            cell.absorb(d_ref)

            return cell

        def export_params(self):

            t_pad=self.pad.export_params()
            t_pad.pop("Name")

            t_pad=add_prefix_dict(t_pad,"Pad")

            t=cls.export_params(self)

            t.update(t_pad)

            return t

        def import_params(self, df):

            cls.import_params(self,df)

            if_match_import(self.pad,df,"Pad")

        @property
        def resistance_squares(self):

            r0=super().resistance_squares

            for port in cls.draw(self).get_ports():

                self.pad.port=port

                r0=r0+self.pad.resistance_squares

            return r0

    addPad.__name__=" ".join([cls.__name__,"w Pad"])

    return addPad

def addProbe(cls,probe):

    class addProbe(cls):

        gnd_routing_width=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.probe=probe(self.name+"Probe")

            self.gnd_routing_width=LayoutDefault.DUTrouting_width

        def draw(self):

            device_cell=cls.draw(self)

            probe_cell=self.probe.draw()

            cell=Device(name=self.name)

            probe_dut_distance=self.probe_dut_distance

            cell.add_ref(device_cell, alias=self.name+"Device")

            bbox=cell.bbox

            from phidl.device_layout import DeviceReference

            probe_ref=DeviceReference(probe_cell)

            probe_ref.connect(probe_cell.ports['sig'],\
            destination=device_cell.ports['bottom'],overlap=-probe_dut_distance.y)

            dut_port_bottom=device_cell.ports['bottom']

            dut_port_top=device_cell.ports['top']

            bbox=super()._bbox_mod(bbox)

            if isinstance(self.probe,GSGProbe):

                probe_port_lx=probe_ref.ports['gnd_left']
                probe_port_center=probe_ref.ports['sig']
                probe_port_rx=probe_ref.ports['gnd_right']

                routing_lx=self._route(bbox,probe_port_lx,dut_port_top)

                r_lx_cell=routing_lx.draw()

                routing_rx=self._route(bbox,probe_port_rx,dut_port_top)

                r_rx_cell=routing_rx.draw()

                routing_gnd=pg.boolean(r_lx_cell,r_rx_cell,'or',layer=self.probe.layer)

                routing_c=pg.compass(size=(self.anchor.metalized.x,\
                    probe_dut_distance.y),layer=self.probe.layer)

                center_routing=DeviceReference(routing_c)

                center_routing.connect(center_routing.ports['S'],destination=dut_port_bottom)

                routing_tot=routing_gnd.add(center_routing)

            elif isinstance(self.probe,GSProbe):

                raise ValueError("DUT with GSprobe to be implemented ")

            else:

                raise ValueError("DUT without GSG/GSprobe to be implemented ")

            if hasattr(self,'_stretch_top_margin'):

                if self._stretch_top_margin:

                    patch_top=pg.rectangle(\
                    size=(dut_port_top.width,cell.ymax-dut_port_top.midpoint[1]),\
                    layer=self.probe.layer)

                    patch_top.move(origin=(patch_top.x,0),\
                        destination=dut_port_top.midpoint)

                    routing_tot.add(patch_top)

            routing_tot=join(routing_tot.add(probe_ref)).flatten()

            cell.add_ref(routing_tot,alias=self.name+'Probe')



            return cell

        def _route(self,bbox,p1,p2):

            routing=Routing()

            routing.layer=self.probe.layer

            routing.clearance=bbox

            routing.trace_width=self.gnd_routing_width

            routing.ports=tuple(copy(x) for x in [p1,p2])

            return routing

        def export_params(self):

            t=cls.export_params(self)

            t_probe=self.probe.export_params()

            t_probe=add_prefix_dict(t_probe,'Probe')

            t.update(t_probe)

            return t

        def import_params(self,df):

            cls.import_params(self,df)

            if_match_import(self.probe,df,"Probe")

        def export_all(self):

            df=super().export_all()
            df["DUTResistance"]=super().resistance_squares
            df["ProbeResistance"]=self.probe_resistance_squares

            return df

        @property

        def resistance_squares(self):

            return super().resistance_squares+self.probe_resistance_squares

        @property

        def probe_resistance_squares(self):

            device_cell=cls.draw(self)

            dut_port_bottom=device_cell.ports['bottom']

            dut_port_top=device_cell.ports['top']

            bbox=device_cell.bbox

            bbox=super()._bbox_mod(bbox)

            probe_cell=self.probe.draw()

            if isinstance(self.probe,GSGProbe):

                probe_port_lx=probe_cell.ports['gnd_left']
                probe_port_center=probe_cell.ports['sig']
                probe_port_rx=probe_cell.ports['gnd_right']

            routing_lx=self._route(bbox,probe_port_lx,dut_port_top)

            routing_lx_len=routing_lx.path.length()

            routing_rx=self._route(bbox,probe_port_rx,dut_port_top)

            routing_rx_len=routing_rx.path.length()

            r_probe=(routing_lx_len/self.gnd_routing_width+\
                routing_rx_len/self.gnd_routing_width)/2+\
                self.probe_dut_distance.y/self.anchor.metalized.x

            return r_probe

        @property
        def probe_dut_distance(self):
            return Point(0,self.idt.active_area.x/2)

    addProbe.__name__=" ".join([cls.__name__,"w Probe"])

    return addProbe

def addLargeGnd(probe):

    class addLargeGnd(probe):

        ground_size=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            probe.__init__(self,*args,**kwargs)

            self.ground_size=LayoutDefault.GSGProbe_LargePadground_size

        def draw(self):

            cell=Device(name=self.name)

            oldprobe=cell<<probe.draw(self)

            cell.absorb(oldprobe)

            groundpad=pg.compass(size=(self.ground_size,self.ground_size),\
            layer=self.layer)

            [_,_,ul,ur]=get_corners(groundpad)

            for name,p in oldprobe.ports.items():

                name=p.name

                if 'gnd' in name:

                    groundref=cell<<groundpad

                    if 'left' in name:

                        groundref.move(origin=ur(),\
                        destination=p.endpoints[1])

                        left_port=groundref.ports['N']

                    elif 'right' in name:

                        groundref.move(origin=ul(),\
                        destination=p.endpoints[0])

                        right_port=groundref.ports['N']

                    cell.absorb(groundref)

                else :

                    cell.add_port(p)

            for name,port in oldprobe.ports.items():

                if 'gnd' in name:

                    if 'left' in name:

                        left_port=Port(name=name,\
                            midpoint=(left_port.midpoint[0]+self.ground_size/2,\
                            left_port.midpoint[1]-self.ground_size/2),\
                            orientation=180,\
                            width=self.ground_size)

                        cell.add_port(left_port)

                    elif 'right' in name:

                        right_port=Port(name=name,\
                        midpoint=(right_port.midpoint[0]-self.ground_size/2,\
                            right_port.midpoint[1]-self.ground_size/2),\
                        orientation=0,\
                        width=self.ground_size)

                        cell.add_port(right_port)

            return cell

    addLargeGnd.__name__=" ".join([probe.__name__,"w Large Ground"])

    return addLargeGnd

def array(cls,n):

    if not isinstance(n,int):

        raise ValueError(" n needs to be integer")

    class array(cls):

        bus_ext_length=LayoutParamInterface()

        n_blocks=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.bus_ext_length=30

            self.n_blocks=n

        def draw(self):

            unit_cell=cls.draw(self)

            port_names=list(unit_cell.ports.keys())

            cell=draw_array(unit_cell,\
                self.n_blocks,1)

            cell.name=self.name

            lx_bottom=cell.ports[port_names[1]+str(0)]
            rx_bottom=cell.ports[port_names[1]+str(self.n_blocks-1)]

            xsize_bottom=rx_bottom.midpoint[0]+rx_bottom.width/2-\
                (lx_bottom.midpoint[0]-lx_bottom.width/2)

            ydist=cell.ysize

            bus_bottom=pg.compass(size=(xsize_bottom,self.bus_ext_length),\
                layer=self.idt.layer)

            bus_bottom.move(origin=bus_bottom.ports['N'].midpoint,\
                destination=(cell.center[0],cell.ymin))

            lx_top=cell.ports[port_names[0]+str(0)]
            rx_top=cell.ports[port_names[0]+str(self.n_blocks-1)]

            xsize_top=rx_top.midpoint[0]+rx_top.width/2-\
                (lx_top.midpoint[0]-lx_top.width/2)

            bus_top=pg.compass(size=(xsize_top,self.bus_ext_length),\
                layer=self.idt.layer)

            bus_top.move(origin=bus_top.ports['S'].midpoint,\
                destination=(cell.center[0],cell.ymax))

            cell<<bus_bottom

            cell<<bus_top

            cell.flatten()

            cell.add_port(port=bus_bottom.ports["S"],name="bottom")

            cell.add_port(port=bus_top.ports["N"],name="top")

            return cell

        @property
        def resistance_squares(self):

            r=super().resistance_squares

            cell=cls.draw(self)

            for p in cell.get_ports():

                if 'bottom' in p.name:

                    p_bot=p

                    break

            w=p_bot.width

            l=self.bus_ext_length

            n_blocks=self.n_blocks

            if n_blocks==1:

                return r+l/w

            else:

                x_dist=self.idt.active_area.x+self.etchpit.x*2

                if n_blocks%2==1 :

                    return parallel_res(r+l/w,(r+2*x_dist/l)/(n_blocks-1))

                if n_blocks%2==0 :

                    if n_blocks==2:

                        return (r+x_dist/l)/2

                    else:

                        return parallel_res((r+x_dist/l)/2,(r+2*x_dist/l)/(n_blocks-2))

        def export_all(self):

            df=super().export_all()

            df["SingleDeviceResistance"]=super().resistance_squares

            return df

    array.__name__= " ".join([f"{n} array of ",cls.__name__])

    return array

def calibration(cls,type='open'):

    class calibration(cls):

        fixture_type=LayoutParamInterface('short','open')

        def __init__(self,*a,**k):

            super().__init__(*a,**k)

            self.fixture_type=type

        def draw(self):

            cell=Device(name=self.name)

            ref=cell.add_ref(cls.draw(self))

            cell.flatten()

            type=self.fixture_type

            ports=ref.ports

            cell.flatten()

            if type=='open':

                cell.remove_polygons(lambda pts,layer,datatype: not layer== LayoutDefault.layerEtch)

            if type=='short':

                cell.remove_polygons(lambda pts,layer,datatype: not layer== LayoutDefault.layerEtch)

                top_port=ref.ports['top']
                bottom_port=ref.ports['bottom']

                short=pg.taper(length=top_port.y-bottom_port.y,\
                width1=top_port.width,\
                width2=bottom_port.width,layer=self.idt.layer)

                s_ref=cell<<short

                s_ref.connect(short.ports[1],\
                    destination=top_port)

                s_ref.rotate(center=top_port.center,\
                angle=180)
                cell.absorb(s_ref)

            [cell.add_port(port=p,name=n) for n,p in ports.items()]

            return cell

        @property
        def resistance_squares(self):

            type=self.fixture_type

            if type=='open':

                from numpy import Inf
                return Inf

            elif type=='short':

                cell=cls.draw(self)

                ports=cell.get_ports()

                top_port=cell.ports['top']
                bottom_port=cell.ports['bottom']

                l=top_port.y-bottom_port.y
                w=(top_port.width+bottom_port.width)/2

                return l/w

    calibration.__name__=f"{type} fixture for {cls.__name__}"

    return calibration

def bondstack(cls,n,sharedpad=False):

    if not isinstance(n,int):

        raise ValueError(" n needs to be integer")

    padded_cls=addPad(cls)

    class bondstack(padded_cls):

        n_copies=LayoutParamInterface()

        sharedpad=LayoutParamInterface(True,False)

        def __init__(self,*a,**k):

            padded_cls.__init__(self,*a,**k)
            self.n_copies=n
            self.sharedpad=sharedpad


        def draw(self):

            cell=padded_cls.draw(self)

            return cell

    bondstack.__name__=" ".join([f"Bondstack of {n}",padded_cls.__name__])

    return bondstack

class LFERes(LayoutPart):

    __components={'IDT':IDT,"Bus":Bus,"EtchPit":EtchPit,"Anchor":Anchor}

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        for p,cls in self.__components.items():

            setattr(self,p.lower(),cls(name=self.name+p))

        self._set_relations()

        self._stretch_top_margin=False

    def draw(self):

        self._set_relations()

        idt_cell=self.idt.draw()

        cell=Device(self.name)

        idt_ref=cell<<idt_cell

        idt_top_port=idt_ref.ports['top']

        idt_bottom_port=idt_ref.ports['bottom']

        bus_cell = self.bus.draw()

        bus_ref= cell<<bus_cell

        bus_ref.connect(port=bus_cell.ports['conn'],\
        destination=idt_bottom_port)

        etch_cell=self.etchpit.draw()

        etch_ref=cell<<etch_cell

        cell.absorb(bus_ref)

        etch_ref.connect(etch_ref.ports['bottom'],\
        destination=idt_ref.ports['bottom'],\
        overlap=-self.bus.size.y-self.anchor.etch_margin.y)

        cell.absorb(etch_ref)

        anchor_cell=self.anchor.draw()

        anchor_bottom=cell<<anchor_cell

        anchor_bottom.connect(anchor_bottom.ports['conn'],
        destination=idt_ref.ports['bottom'],overlap=-self.bus.size.y)

        if not self._stretch_top_margin:

            anchor_top=(cell<<anchor_cell)

        else:

            anchor_top_dev=deepcopy(self.anchor)

            anchor_top_dev.etch_margin.x=0.5*self.idt.pitch

            anchor_top=cell<<anchor_top_dev.draw()

            del anchor_top_dev

        anchor_top.connect(anchor_top.ports['conn'],\
            idt_ref.ports['top'],overlap=-self.bus.size.y)

        cell.absorb(idt_ref)

        outport_top=anchor_top.ports['conn']
        outport_bottom=anchor_bottom.ports['conn']
        outport_top.name='top'
        outport_top.orientation=90
        outport_bottom.name='bottom'
        outport_bottom.orientation=-90
        outport_top.midpoint=(\
            outport_top.x,\
            outport_top.y+self.anchor.metalized.y)
        outport_bottom.midpoint=(\
            outport_bottom.x,\
            outport_bottom.y-self.anchor.metalized.y)

        cell.absorb(anchor_top)
        cell.absorb(anchor_bottom)

        cell.flatten()

        cell.add_port(outport_top)
        cell.add_port(outport_bottom)

        del idt_cell,bus_cell,etch_cell,anchor_cell

        return cell

    def export_params(self):

        self._set_relations()

        t=super().export_params()

        t_res=self.idt.export_params()
        t_res=pop_all_dict(t_res,["Name","Type"])
        t_res=add_prefix_dict(t_res,"IDT")

        t_bus=self.bus.export_params()
        t_bus=pop_all_dict(t_bus, ['Name','Type','DistanceX','DistanceY','SizeX'])
        t_bus=add_prefix_dict(t_bus,"Bus")

        t_etch=self.etchpit.export_params()
        t_etch=pop_all_dict(t_etch,['Name','Type','ActiveAreaX','ActiveAreaY'])
        t_etch=add_prefix_dict(t_etch,"Etch")

        t_anchor=self.anchor.export_params()
        t_anchor=pop_all_dict(t_anchor,['Name','Type','EtchX','XOffset','EtchChoice'])
        t_anchor=add_prefix_dict(t_anchor,'Anchor')

        t.update(t_res)
        t.update(t_bus)
        t.update(t_etch)
        t.update(t_anchor)

        return t

    def import_params(self,df):

        super().import_params(df)

        for name in self.__components.keys():

            if_match_import(getattr(self,name.lower()),df,name)

        self._set_relations()

    def _set_relations(self):

        self.bus.size=Point(\
            self.idt.active_area.x-\
            2*self.idt.active_area_margin-\
            self.idt.pitch*(1-self.idt.coverage),\
            self.bus.size.y)

        self.bus.distance=Point(\
            0,self.idt.active_area.y+self.bus.size.y)

        self.bus.layer=self.idt.layer

        self.etchpit.active_area=Point(self.idt.active_area.x,\
            self.idt.active_area.y+2*self.bus.size.y+self.anchor.etch_margin.y*2)

        self.anchor.etch_x=self.etchpit.x*2+self.etchpit.active_area.x

        self.anchor.layer=self.idt.layer

        if self.anchor.metalized.x>self.bus.size.x:

            self.anchor.etch_margin.x=(self.bus.size.x-self.anchor.size.x)/2
            warnings.warn("Anchor metal is too wide, reduced to match Bus width size")

    @property
    def resistance_squares(self):

        self.draw()

        ridt=self.idt.resistance_squares
        rbus=self.bus.resistance_squares
        ranchor=self.anchor.resistance_squares

        return ridt+rbus+ranchor

    def export_all(self):

        df=super().export_all()

        df["IDTResistance"]=self.idt.resistance_squares
        df["AnchorResistance"]=self.anchor.resistance_squares
        df["BusResistance"]=self.idt.resistance_squares

        return df

    @property
    def area_aspect_ratio(self):

        cell=LFERes.draw(self)

        width=cell.xsize-2*self.etchpit.x
        height=cell.ysize-self.anchor.etch_margin.y-2*self.anchor.size.y

        return height/width

    @classmethod
    def get_class_param(self):

        param=LayoutPart.get_class_param()

        for prefix,cls in self.__components.items():

            [param.append(prefix+x) for x in cls.get_class_param()]

        return param

    def __getattr__(self,name):

        for p in self.__components.keys():

            if name.startswith(p):

                return getattr(\
                    getattr(self,p.lower()),\
                    name.replace(p,''))

        else:

            raise AttributeError

class FBERes(LFERes):

    plate_position=LayoutParamInterface(\
        'in, short','out, short','in, long','out, long')

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.plate_position='out, short'

        self.platelayer=LayoutDefault.FBEResplatelayer

    def draw(self):

        cell=Device(name=self.name)

        lfe_res=cell.add_ref(LFERes.draw(self))

        if self.plate_position=='out, short':

            plate=pg.rectangle(size=(self.etchpit.active_area.x+8*self.idt.active_area_margin,self.idt.length-self.idt.y_offset/2),\
            layer=self.platelayer)

            plate_ref=cell<<plate

            transl_rel=Point(self.etchpit.x-4*self.idt.active_area_margin,self.anchor.size.y+2*self.anchor.etch_margin.y+self.bus.size.y\
                +self.idt.y_offset*3/4)

            lr_cell=get_corners(cell)[0]
            lr_plate=get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate(),\
            destination=(lr_plate+lr_cell+transl_rel)())

            cell.absorb(plate_ref)

            del plate

        elif self.plate_position=='in, short':

            plate=pg.rectangle(\
                size=(\
                    self.etchpit.active_area.x-\
                        2*self.idt.active_area_margin,\
                        self.idt.length-self.idt.y_offset/2),\
                layer=self.platelayer)

            plate_ref=cell<<plate

            transl_rel=Point(self.etchpit.x+\
                    self.idt.active_area_margin,\
                self.anchor.size.y+\
                2*self.anchor.etch_margin.y+\
                self.bus.size.y+\
                self.idt.y_offset*3/4)

            lr_cell=get_corners(cell)[0]
            lr_plate=get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate(),\
            destination=(lr_plate+lr_cell+transl_rel)())

            cell.absorb(plate_ref)

            del plate

        elif self.plate_position=='out, long':

            plate=pg.rectangle(\
                size=(self.etchpit.active_area.x+\
                        8*self.idt.active_area_margin,\
                    self.idt.length+\
                        2*self.bus.size.y+\
                        self.idt.y_offset),\
                layer=self.platelayer)

            plate_ref=cell<<plate

            transl_rel=Point(self.etchpit.x-\
                4*self.idt.active_area_margin,\
                    self.anchor.size.y+2*self.anchor.etch_margin.y)

            lr_cell=get_corners(cell)[0]
            lr_plate=get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate(),\
            destination=(lr_plate+lr_cell+transl_rel)())

            cell.absorb(plate_ref)

            del plate

        elif self.plate_position=='in, long':

            plate=pg.rectangle(\
                size=(\
                    self.etchpit.active_area.x-\
                        2*self.idt.active_area_margin,\
                        self.idt.length+\
                            2*self.bus.size.y+\
                            self.idt.y_offset),
                layer=self.platelayer)

            plate_ref=cell<<plate

            transl_rel=Point(self.etchpit.x+\
                    self.idt.active_area_margin,\
                        self.anchor.size.y+2*self.anchor.etch_margin.y)

            lr_cell=get_corners(cell)[0]
            lr_plate=get_corners(plate_ref)[0]

            plate_ref.move(origin=lr_plate(),\
            destination=(lr_plate+lr_cell+transl_rel)())

            cell.absorb(plate_ref)

            del plate

        cell.absorb(lfe_res)
        for name,port in lfe_res.ports.items():

            cell.add_port(port,name)

        return cell

class TFERes(LFERes):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.bottomlayer=LayoutDefault.TFEResbottomlayer

    def draw(self):

        cell=Device(name=self.name)

        cell.add_ref(LFERes.draw(self))

        idt_bottom=copy(self.idt)

        idt_bottom.layer=self.bottomlayer

        idt_ref=cell<<idt_bottom.draw()

        p_bott=idt_ref.ports['bottom']

        p_bott_coord=Point().from_iter(p_bott.midpoint)

        idt_ref.mirror(p1=(p_bott_coord-Point(p_bott.width/2,0))(),\
            p2=(p_bott_coord+Point(p_bott.width/2,0))())

        idt_ref.move(origin=(idt_ref.xmin,idt_ref.ymax),\
            destination=(idt_ref.xmin,idt_ref.ymax+self.idt.length+self.idt.y_offset))

        bus_bottom=copy(self.bus)

        bus_bottom.layer=self.bottomlayer

        bus_ref=cell<<bus_bottom.draw()

        bus_ref.move(origin=(0,0),\
        destination=(0,-self.bus.size.y))

        cell.absorb(bus_ref)

        anchor_bottom=copy(self.anchor)

        anchor_bottom.layer=self.bottomlayer
        anchor_bottom.etch_choice=False

        anchor_ref=cell<<anchor_bottom.draw()

        anchor_ref.connect(anchor_ref.ports['conn'],\
            destination=idt_ref.ports['top'],\
            overlap=-self.bus.size.y)

        cell.absorb(anchor_ref)

        anchor_ref_2=cell<<anchor_bottom.draw()

        anchor_ref_2.connect(anchor_ref_2.ports['conn'],\
            destination=idt_ref.ports['bottom'],\
            overlap=-self.bus.size.y)

        cell.absorb(anchor_ref_2)

        cell.absorb(idt_ref)

        out_ports=cell.get_ports()

        for p in out_ports:

            cell.add_port(p)

        return cell

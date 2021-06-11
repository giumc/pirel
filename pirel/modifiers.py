import pirel.pcells as pc

import pirel.tools as pt

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray,Device,DeviceReference

from pirel.tools import *

import pandas as pd

import warnings

from copy import copy

def Scaled(cls):

    ''' Class Decorator that accept normalized parameters for resonator designs.

    Descaling rules:
        IDT gap (d) = IDT gap (n) * pitch
        Bus length (d) = Bus length (n) * pitch
        Etch pit width (d) = Etch pit width (d) * active region width
        Anchor width (d) = Anchor width (n) * active region width
        Anchor length (d) = Anchor length (n) * pitch
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

            # self.idt.length=self.idt.length/p

            self.bus.size=Point(self.bus.size.x,self.bus.size.y/p)

            self.etchpit.x=self.etchpit.x/active_area_x

            self.anchor.size=Point(\
                self.anchor.size.x/active_area_x,\
                self.anchor.size.y/p)

            self._normalized=True

        def _denormalize(self):

            if self._normalized==False:

                raise ValueError("Already denormalized")

            p=self.idt.pitch

            self.idt.y_offset=self.idt.y_offset*p

            self.bus.size=Point(self.bus.size.x,self.bus.size.y*p)

            active_area_x=self.idt.active_area.x

            self.etchpit.x=self.etchpit.x*active_area_x

            self.anchor.size=Point(\
                self.anchor.size.x*active_area_x,\
                self.anchor.size.y*p)

            self._normalized=False

            return self

    Scaled.__name__=" ".join(["Scaled",cls.__name__])

    # Scaled.draw=cached(Scaled)(Scaled.draw)

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

        pad_layers : lenght 2 iterable of int
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

        over_via=LayoutParamInterface()

        via_distance=LayoutParamInterface()

        via_area=LayoutParamInterface()

        pad_layers=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.pad_layers=[LayoutDefault.layerTop,LayoutDefault.layerBottom]

            self.over_via=LayoutDefault.addVia_over_via

            self.via_distance=LayoutDefault.addVia_via_distance

            self.via_area=LayoutDefault.addVia_via_area

        def draw(self):

            cell=Device(name=self.name)

            super_ref=cell.add_ref(cls.draw(self))

            nvias_x,nvias_y=self.n_vias

            unit_cell=self._draw_padded_via()

            viacell=join(CellArray(unit_cell,\
                columns=nvias_x,rows=nvias_y,\
                spacing=(unit_cell.xsize,unit_cell.ysize)))

            viacell.add_port(Port(name='conn',\
                midpoint=(viacell.x,viacell.ymax),\
                width=viacell.xsize,\
                orientation=90))

            for sides in side:

                for p_name in super_ref.ports.keys():

                    if re.search(sides,p_name):

                        p=super_ref.ports[p_name]

                        pad=pg.compass(size=(p.width,self.via_distance),layer=self.pad_layers[0])

                        if sides=='top':

                            self._attach_instance(cell, pad, pad.ports['S'], viacell,p)

                        if sides=='bottom':

                            self._attach_instance(cell, pad, pad.ports['N'], viacell,p)

            for p_name,p_value in super_ref.ports.items():

                cell.add_port(p_value)

            return cell

        def export_params(self):

            t=cls.export_params(self)

            pop_all_dict(t,['ViaName'])


            return t

        def _bbox_mod(self,bbox):

            LayoutPart._bbox_mod(self,bbox)

            ll=Point(bbox[0])

            ur=Point(bbox[1])

            nvias_x,nvias_y=self.n_vias

            if any([_=='top' for _ in side]):

                ur=ur-Point(0,float(self.via.size*self.over_via*nvias_y+self.via_distance))

            if any([_=='bottom' for _ in side]):

                ll=ll+Point(0,float(self.via.size*self.over_via*nvias_y+self.via_distance))

            return (ll.coord,ur.coord)

        def _draw_padded_via(self):

            viaref=DeviceReference(self.via.draw())

            size=float(self.via.size*self.over_via)

            port=viaref.ports['conn']

            trace=pg.rectangle(size=(size,size),layer=self.pad_layers[0])

            trace.move(origin=trace.center,\
                destination=viaref.center)

            trace2=pg.copy_layer(trace,layer=self.pad_layers[0],new_layer=self.pad_layers[1])

            cell=Device(self.name)

            cell.absorb(cell<<trace)

            cell.absorb(cell<<trace2)

            cell.add(viaref)

            port.midpoint=(port.midpoint[0],cell.ymax)

            port.width=size

            cell.add_port(port)

            if bottom_conn==False:

                cell.remove_layers(layers=[self.pad_layers[1]])

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

        @staticmethod
        def get_components():

            supercomp=copy(cls.get_components())

            supercomp.update({"Via":pc.Via})

            return supercomp

        @property
        def n_vias(self):

            import numpy as np

            nvias_x=max(1,int(np.floor(self.via_area.x/self.via.size/self.over_via)))
            nvias_y=max(1,int(np.floor(self.via_area.y/self.via.size/self.over_via)))

            return nvias_x,nvias_y

    addVia.__name__=" ".join([cls.__name__,"w Via"])

    # addVia.draw=cached(addVia)(addVia.draw)

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

        def draw(self):

            cell=Device()

            cell.name=self.name

            d_ref=cell.add_ref(cls.draw(self))

            for name,port in d_ref.ports.items():

                self.pad.port=port

                pad_ref=cell.add_ref(self.pad.draw())

                pad_ref.connect(pad_ref.ports['conn'],
                    destination=port)

                cell.absorb(pad_ref)

                cell.add_port(port,name)

            return cell

        @staticmethod
        def get_components():

            supercomp=copy(cls.get_components())

            supercomp.update({"Pad":pc.Pad})

            return supercomp

        @property
        def resistance_squares(self):

            r0=super().resistance_squares

            for port in cls.draw(self).get_ports():

                self.pad.port=port

                r0=r0+self.pad.resistance_squares

            return r0

    # addPad.draw=cached(addPad)(addPad.draw)

    addPad.__name__=" ".join([cls.__name__,"w Pad"])

    return addPad

def addPartialEtch(cls):

    class addPartialEtch(cls):

        @staticmethod
        def get_components():

            original_comp=copy(cls.get_components())

            for compname,comp_value in original_comp.items():

                if comp_value==pc.IDT:

                    original_comp[compname]=pc.PartialEtchIDT

                    break

            else:

                raise TypeError(f" no IDT to modify in {cls.__name__}")

            return original_comp

    return addPartialEtch

    # addPartialEtch.draw=cached(addPartialEtch)(addPartialEtch.draw)

    adddPartialEtch.__name__=cls.__name__+' w PartialEtching'

def addProbe(cls,probe=pc.GSGProbe):

    class addProbe(cls):

        gnd_routing_width=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.gnd_routing_width=100.0

            self._setup_routings()

        def draw(self):

            self._setup_routings()

            device_cell=cls.draw(self)

            probe_cell=self.probe.draw()

            cell=Device(name=self.name)

            cell.add_ref(device_cell, alias=self.name+"Device")

            probe_ref=cell.add_ref(probe_cell, alias=self.name+"Probe")

            self._move_probe_ref(probe_ref)

            cell.add_ref(self._draw_probe_routing(),alias=self.name+"GndTrace")

            return cell

        def export_params(self):

            t=cls.export_params(self)

            pop_all_dict(t, ["ProbeName"])

            pop_all_dict(t, [k for k in t if re.search('SigTrace',k) ])
            pop_all_dict(t, [k for k in t if re.search('GndLeftTrace',k) ])
            pop_all_dict(t, [k for k in t if re.search('GndRightTrace',k) ])

            return t

        def export_all(self):

            df=super().export_all()
            df["DUTResistance"]=super().resistance_squares
            df["ProbeResistance"]=self.probe_resistance_squares

            return df

        @property
        def resistance_squares(self):

            return super().resistance_squares

        @staticmethod
        def get_components():

            supercomp=copy(cls.get_components())

            if issubclass(probe,pc.GSGProbe):

                supercomp.update({
                    "Probe":probe,
                    "SigTrace":pc.ParasiticAwareMultiRouting,
                    "GndLeftTrace":pc.MultiRouting,
                    "GndRightTrace":pc.MultiRouting})

            else:

                raise ValueError("To be implemented")

            return supercomp

        @property
        def probe_resistance_squares(self):

            return 0

        @property
        def probe_dut_distance(self):

            return Point(0,self.idt.active_area.x/2)

        def _move_probe_ref(self,probe_ref):

            probe_dut_distance=self.probe_dut_distance

            device_cell=cls.draw(self)

            for p_name in device_cell.ports.keys():

                if re.search('bottom',p_name):

                    probe_ref.move(origin=(probe_ref.center[0],probe_ref.ymax),\
                    destination=(\
                        device_cell.center[0],\
                        device_cell.ports[p_name].midpoint[1]-probe_dut_distance.y))

                    break

            else:

                raise ValueError(f"no bottom port in {cls.__name__} cell")

            return probe_ref

        def _setup_routings(self):

            device_cell=cls.draw(self)

            probe_cell=self.probe.draw()

            probe_ref=self._move_probe_ref(DeviceReference(probe_cell))

            bbox=super()._bbox_mod(device_cell.bbox)

            if isinstance(self.probe,pc.GSGProbe):

                for index,groundroute in enumerate([self.gndlefttrace,self.gndrighttrace]):

                    groundroute.layer=self.probe.layer

                    groundroute.clearance=bbox

                    groundroute.trace_width=self.gnd_routing_width

                    if index==0:

                        groundroute.side='left'

                        groundroute.source=(probe_ref.ports['gnd_left'],)

                    elif index==1:

                        groundroute.side='right'

                        groundroute.source=(probe_ref.ports['gnd_right'],)

                    device_ports=device_cell.ports

                    dut_port_top=[]

                    for port_name in device_ports.keys():

                        if re.search('top',port_name):

                            dut_port_top.append(device_ports[port_name])

                    groundroute.destination=tuple(dut_port_top)

                #signal routing
                signalroute=self.sigtrace

                for p_name in device_cell.ports.keys():

                    if re.search('bottom',p_name):

                        signalroute.trace_width=device_cell.ports[p_name].width

                        break

                else:

                    raise ValueError(f"no bottom port in {cls.__name__} cell")

                bottom_ports=[]

                for port_name in device_ports.keys():

                    if re.search('bottom',port_name):

                        bottom_ports.append(device_ports[port_name])

                signalroute.layer=self.probe.layer

                signalroute.clearance=bbox

                signalroute.source=(probe_ref.ports['sig'],)

                signalroute.destination=tuple(bottom_ports)

            elif isinstance(self.probe,pc.GSProbe):

                raise ValueError("addProbe with GSprobe to be implemented ")

            else:

                raise ValueError("addProbe without GSG/GSprobe to be implemented ")

        def _draw_probe_routing(self):

            if isinstance(self.probe,pc.GSGProbe):

                routing_cell=Device()

                routing_cell<<self.gndlefttrace.draw()

                routing_cell<<self.gndrighttrace.draw()

                routing_cell<<self.sigtrace.draw()

                return routing_cell

            else :

                raise ValueError("To be implemented")

    addProbe.__name__=" ".join([cls.__name__,"w Probe"])

    # addProbe.draw=cached(addProbe)(addProbe.draw)

    return addProbe

def addLargeGnd(probe):

    class addLargeGnd(probe):

        ground_size=LayoutParamInterface()

        pad_position=LayoutParamInterface('top','side')

        def __init__(self,*args,**kwargs):

            probe.__init__(self,*args,**kwargs)

            self.ground_size=LayoutDefault.GSGProbe_LargePadground_size

            self.pad_position='side'

        def draw(self):

            cell=pt.Device(name=self.name)

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

                        groundref.move(origin=ur.coord,\
                        destination=p.endpoints[1])

                        left_port=groundref.ports['N']

                    elif 'right' in name:

                        groundref.move(origin=ul.coord,\
                        destination=p.endpoints[0])

                        right_port=groundref.ports['N']

                    cell.absorb(groundref)

                else :

                    cell.add_port(p)

            for name,port in oldprobe.ports.items():

                if 'gnd' in name:

                    if 'left' in name:

                        if self.pad_position=='side':

                            left_port=Port(name=name,\
                                midpoint=(left_port.midpoint[0]+self.ground_size/2,\
                                left_port.midpoint[1]-self.ground_size/2),\
                                orientation=180,\
                                width=self.ground_size)

                        elif self.pad_position=='top':

                            left_port=Port(name=name,\
                                midpoint=(left_port.midpoint[0],\
                                left_port.midpoint[1]),\
                                orientation=90,\
                                width=self.ground_size)

                        else :

                            raise ValueError(f"New pad position is {self.pad_position} : not acceptable")

                        cell.add_port(left_port)

                    elif 'right' in name:

                        if self.pad_position=='side':

                            right_port=Port(name=name,\
                            midpoint=(right_port.midpoint[0]-self.ground_size/2,\
                                right_port.midpoint[1]-self.ground_size/2),\
                            orientation=0,\
                            width=self.ground_size)

                        elif self.pad_position=='top':

                            right_port=Port(name=name,\
                            midpoint=(right_port.midpoint[0],\
                                right_port.midpoint[1]),\
                            orientation=90,\
                            width=self.ground_size)

                        else :

                            raise ValueError(f"New pad position is {self.pad_position} : not acceptable")

                        cell.add_port(right_port)

            return cell

    # addLargeGnd.draw=pt.cached(addLargeGnd)(addLargeGnd.draw)

    addLargeGnd.__name__=" ".join([probe.__name__,"w Large Ground"])

    return addLargeGnd

def array(cls,n=2):

    if not isinstance(n,int):

        raise ValueError(" n needs to be integer")

    class array(cls):

        n_blocks=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.n_blocks=n

        def draw(self):

            unit_cell=cls.draw(self)

            port_names=list(unit_cell.ports.keys())

            cell=draw_array(unit_cell,\
                self.n_blocks,1)

            cell.name=self.name

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

            l=w

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

    array.__name__= " ".join([f"{n} array of",cls.__name__])

    return array

def fixture(cls,style='open'):

    class fixture(cls):

        style=LayoutParamInterface('short','open')

        def __init__(self,*a,**k):

            super().__init__(*a,**k)

            self.style=style

        def draw(self):

            supercell=cls.draw(self)

            cell=pg.deepcopy(supercell)

            style=self.style

            ports=supercell.ports

            for subcell in cell.get_dependencies(recursive=True):

                if 'IDT' in subcell.aliases:

                    idt_parent=subcell
                    idt_cell=subcell['IDT']

            for alias in cell.aliases.keys():

                if 'IDT' in alias:

                    idt_parent=cell
                    idt_cell=cell['IDT']

            if style=='open':

                idt_parent.remove(idt_cell)

            if style=='short':

                top_port=idt_cell.ports['top']

                bottom_port=idt_cell.ports['bottom']

                short=pg.taper(length=top_port.y-bottom_port.y,\
                width1=top_port.width,\
                width2=bottom_port.width,layer=self.idt.layer)

                s_ref=cell<<short

                s_ref.connect(short.ports[1],\
                    destination=top_port)

                s_ref.rotate(center=top_port.center,\
                angle=180)

                cell.absorb(s_ref)

            return cell

        @property
        def resistance_squares(self):

            style=self.style

            if style=='open':

                from numpy import Inf
                return 1e9

            elif style=='short':

                cell=cls.draw(self)

                ports=cell.get_ports()

                top_port=cell.ports['top']
                bottom_port=cell.ports['bottom']

                l=top_port.y-bottom_port.y
                w=(top_port.width+bottom_port.width)/2

                return l/w

    fixture.__name__=f"fixture for {cls.__name__}"

    return fixture

def bondstack(cls,n=4,sharedpad=False):

    if not isinstance(n,int):

        raise ValueError(" n needs to be integer")

    padded_cls=addPad(cls)

    class bondstack(padded_cls):

        n_copies=LayoutParamInterface()

        sharedpad=LayoutParamInterface(True,False)

        pitch=LayoutParamInterface()

        def __init__(self,*a,**k):

            padded_cls.__init__(self,*a,**k)
            self.n_copies=n
            self.sharedpad=sharedpad
            self.pitch=150.0

        def draw(self):

            cell=padded_cls.draw(self)

            return pt.draw_array(cell,n,1,0.0,self.pitch)

    bondstack.__name__=" ".join([f"Bondstack of {n}",padded_cls.__name__])

    return bondstack

_allmodifiers=(Scaled,addVia,addPad,addPartialEtch,addProbe,addLargeGnd,array,fixture,bondstack)

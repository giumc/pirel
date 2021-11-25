import pirel.pcells as pc

import pirel.tools as pt

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray,Device,DeviceReference,Group

from pirel.tools import Point,LayoutDefault,LayoutParamInterface,LayoutPart

import pirel.addOns.standard_parts as ps

import pdb

import pandas as pd

import numpy as np

import warnings, re

from copy import copy,deepcopy

# Classes decorators

def makeScaled(cls):

    ''' Class Decorator that accept normalized parameters for resonator designs.

    Descaling rules:
        IDT gap (d) = IDT gap (n) * pitch
        Bus length (d) = Bus length (n) * pitch
        Etch pit width (d) = Etch pit width (d) * active region width
        Anchor width (d) = Anchor width (n) * active region width
        Anchor length (d) = Anchor length (n) * pitch
        Anchor metal X (d) = Anchor metal X (n) * Anchor width
        Anchor metal Y (d) = Anchor metal Y (n) * Anchor length.

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

        def _set_params(self,df):

            self._normalize()

            cls._set_params(self,df)

            self._denormalize()

        def get_params(self):

            self._normalize()

            df=cls.get_params(self)

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

            self.bus.size=pt.Point(self.bus.size.x,self.bus.size.y/p)

            self.etchpit.x=self.etchpit.x/active_area_x

            self.anchor.size=pt.Point(
                self.anchor.size.x/active_area_x,
                self.anchor.size.y/p)

            self.anchor.metalized=pt.Point(
                self.anchor.metalized.x/anchor_x,
                self.anchor.metalized.y/anchor_y)

            self._normalized=True

        def _denormalize(self):

            if self._normalized==False:

                raise ValueError("Already denormalized")

            p=self.idt.pitch

            self.idt.y_offset=self.idt.y_offset*p

            self.bus.size=pt.Point(self.bus.size.x,self.bus.size.y*p)

            active_area_x=self.idt.active_area.x

            self.etchpit.x=self.etchpit.x*active_area_x

            self.anchor.size=pt.Point(\
                self.anchor.size.x*active_area_x,\
                self.anchor.size.y*p)

            self.anchor.metalized=pt.Point(
                self.anchor.metalized.x*self.anchor.size.x,
                self.anchor.metalized.y*self.anchor.size.y)

            self._normalized=False

            return self

    Scaled.__name__=" ".join(["Scaled",cls.__name__])

    return Scaled

def addPad(cls, pad=pc.Pad, side='top'):
    ''' Class decorator to add probing pads to existing cells.
        Parameters
        ----------
        cls : pirel.LayoutPart
            design where pads have to be added

        Attributes
        ----------
        pad : pirel.Pad
            pad design for the cell

        side : str ( or iterable of str)
            tag for ports
        The pad design needs a port to attach to the existing cell,
            see help for more info.
        '''

    if isinstance(side,str):

        side=[side]

    class Padded(cls):

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

        def draw(self):

            cell=Device(self.name)

            d_ref=cell.add_ref(cls.draw(self),alias='Device')

            for name,port in d_ref.ports.items():

                cell.add_port(port)

            import pdb; pdb.set_trace()

            add_pads(cell,self.pad,side)

            return cell

        @staticmethod
        def get_components():

            supercomp=copy(cls.get_components())

            supercomp.update({"Pad":pad})

            return supercomp

        @property
        def resistance_squares(self):

            r0=super().resistance_squares

            for port in cls.draw(self).get_ports():

                self.pad.port=port

                r0=r0+self.pad.resistance_squares

            return r0

        def _bbox_mod(self,bbox):

            LayoutPart._bbox_mod(self,bbox)

            ll=pt.Point(bbox[0])

            ur=pt.Point(bbox[1])

            if any([_=='top' for _ in side]):

                ur=ur-pt.Point(0,float(self.pad.size+self.pad.distance))

            if any([_=='bottom' for _ in side]):

                ll=ll+pt.Point(0,float(self.pad.size+self.pad.distance))

            return (ll.coord,ur.coord)

    Padded.__name__=" ".join([cls.__name__,"w Pad"])

    return Padded

def addPartialEtch(cls):

    class PartialEtched(cls):

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

    return PartialEtched

    # PartialEtched.draw=cached(PartialEtched)(PartialEtched.draw)

    adddPartialEtch.__name__=cls.__name__+' w PartialEtching'

def addOnePortProbe(cls,probe=pc.GSGProbe):

    class OnePortProbed(cls):
        ''' adds a one port probe to existing LayoutClass.

        Parameters:
        -----------
            cls : pt.LayoutPart
                the layout drawn with this LayoutPart needs to have
                a 'bottom' and 'top' port.

            probe: pt.LayoutPart
                currently working only on pc.GSGProbe.
        '''

        gnd_routing_width=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.gnd_routing_width=100.0

            self._setup_routings(cls.draw(self),self.probe.draw())

        def draw(self):

            device_cell=cls.draw(self)

            self._setup_routings(device_cell)

            probe_cell=self.probe.draw()

            cell=Device(name=self.name)

            cell.add_ref(device_cell, alias=self.name+"Device")

            probe_ref=cell.add_ref(probe_cell, alias=self.name+"Probe")

            self._move_probe_ref(probe_ref)

            routing_cell=self._draw_probe_routing()

            if hasattr(self,'via'):

                routing_cell_vias=add_vias(routing_cell,
                    routing_cell.bbox,
                    self.via,
                    spacing=self.via.size*2,
                    tolerance=self.via.size*1.5)

                cell.add_ref(routing_cell_vias,alias=self.name+"GroundTrace")

            else:

                cell.add_ref(routing_cell,alias=self.name+"GroundTrace")

            return cell

        def get_params(self):

            t=cls.get_params(self)

            pt.pop_all_dict(t, ["ProbeName"])

            pt.pop_all_dict(t, [k for k in t if re.search('SigTrace',k) ])
            pt.pop_all_dict(t, [k for k in t if re.search('GndLeftTrace',k) ])
            pt.pop_all_dict(t, [k for k in t if re.search('GndRightTrace',k) ])

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
                    "GndRightTrace":pc.MultiRouting,
                    "Via":pc.Via})

            else:

                raise ValueError("To be implemented")

            return supercomp

        @property
        def probe_resistance_squares(self):

            return 0

        @property
        def probe_dut_distance(self):

            return self.idt.probe_distance

        def _move_probe_ref(self,device_cell,probe_ref):

            probe_dut_distance=self.probe_dut_distance

            probe_ref.move(
                origin=(probe_ref.center[0],probe_ref.ymax),
                destination=(
                    device_cell.center[0],
                    device_cell.ports['bottom'].midpoint[1]-probe_dut_distance.y))

            return probe_ref

        def _setup_routings(self,device_cell,probe_cell):

            probe_ref=self._move_probe_ref(device_cell,DeviceReference(probe_cell))

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

                raise ValueError("OnePortProbed with GSprobe to be implemented ")

            else:

                raise ValueError("OnePortProbed without GSG/GSprobe to be implemented ")

        def _draw_probe_routing(self):

            if isinstance(self.probe,pc.GSGProbe):

                routing_cell=Device()

                routing_cell<<self.gndlefttrace.draw()

                routing_cell<<self.gndrighttrace.draw()

                routing_cell<<self.sigtrace.draw()

                return routing_cell

            else :

                raise ValueError("To be implemented")

    OnePortProbed.__name__=" ".join([cls.__name__,"w Probe"])

    return OnePortProbed

def addLargeGround(probe):

    class LargeGrounded(probe):

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

            [_,_,ul,ur]=pt.get_corners(groundpad)

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
                                midpoint=(left_port.midpoint[0]-self.ground_size/2,\
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
                            midpoint=(right_port.midpoint[0]+self.ground_size/2,\
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

    # LargeGnd.draw=pt.cached(LargeGnd)(LargeGnd.draw)

    LargeGrounded.__name__=" ".join([probe.__name__,"w Large Ground"])

    return LargeGrounded

def makeArray(cls,n=2):

    if not isinstance(n,int):

        raise ValueError(" n needs to be integer")

    class Arrayed(cls):

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

                    return pt.parallel_res(r+l/w,(r+2*x_dist/l)/(n_blocks-1))

                if n_blocks%2==0 :

                    if n_blocks==2:

                        return (r+x_dist/l)/2

                    else:

                        return pt.parallel_res((r+x_dist/l)/2,(r+2*x_dist/l)/(n_blocks-2))

        def export_all(self):

            df=super().export_all()

            df["SingleDeviceResistance"]=super().resistance_squares

            return df

    Arrayed.__name__= " ".join([f"{n} array of",cls.__name__])

    return Arrayed

def makeFixture(cls,style='open'):

    class Fixture(cls):

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

    Fixture.__name__=f"fixture for {cls.__name__}"

    return Fixture

def makeNpaths(cls, pad=pc.Pad, probe=pc.GSGProbe, n=4):

    if not isinstance(n,int):

        raise ValueError(f"n needs to be integer, {n.__class__.__name__} was passed")

    if not issubclass(pad,LayoutPart):

        raise ValueError(f"pad needs to be a LayoutPart, {pad.__class__.__name__} was passed")

    class NpathsOf(cls):

        n_copies=LayoutParamInterface()

        spacing=LayoutParamInterface()

        comm_pad_length=LayoutParamInterface()

        def __init__(self,*a,**k):

            cls.__init__(self,*a,**k)

            self.n_copies=n

            self.spacing=pt.Point(0,0)

            self.comm_pad_length=0.0

            makeNpaths._set_relations(self)

        def draw(self):

            makeNpaths._set_relations(self)

            cell=pg.deepcopy(cls.draw(self))

            connect_ports(
                cell,
                conn_dist=self.idt.probe_distance,
                tags='top')

            add_pads(cell,self.pad,tags='top')

            out_cell=pg.Device(self.name)

            refs=[]

            for n in range(1,self.n_copies+1):

                refs.append(out_cell.add_ref(cell,alias='Device'+str(n)))

                origin=pt.Point(refs[-1].xmin,refs[-1].ymin)

                transl=pt.Point(n*refs[-1].xsize,0)+n*self.spacing

                refs[-1].move(destination=transl.coord)

                if n%2==0 and n>0:

                    refs[-1].rotate(
                        angle=180,
                        center=(refs[-1].center[0],refs[-1].ymin))

                    refs[-1].move(destination=(0,-self.comm_pad_length))

            comm_pad=pg.rectangle(size=(out_cell.xsize,self.comm_pad_length),layer=self.pad.layer)

            comm_pad_via=add_vias(comm_pad,comm_pad.bbox,self.via,self.via.size*2)

            comm_pad_via.move(origin=(comm_pad.xmin,comm_pad.ymin),
                         destination=(out_cell.xmin,out_cell.ymin+(out_cell.ysize-self.comm_pad_length)/2))

            out_cell.add_ref(comm_pad_via,alias='CommPad')

            return out_cell

        @staticmethod
        def get_components():

            pars=copy(cls.get_components())

            pars.update({
            # "TestDevice":OnePortProbed(cls,probe),
            "Pad":pad,"Via":pc.Via})

            return pars

        def get_params(self):

            pars=copy(cls.get_params(self))

            tbr=[]

            for name in pars:

                if "TestDevice" in name:

                    if not "GndRoutingWidth" in name:

                        tbr.append(name)

                if "PadDistance" in name:

                    tbr.append(name)

            pt.pop_all_dict(pars,tbr)

            return pars

        def _set_relations(self):

            try:

                cls._set_relations(self)

            except:

                pass

            self.pad.distance=0

    NpathsOf.__name__=" ".join([f"{n} paths of",cls.__name__])

    return NpathsOf

def makeTwoPortProbe(cls):

    class TwoPort(cls):

        offset=LayoutParamInterface()

        def __init__(self,*a,**kw):

            if not issubclass(cls,(pc.GSGProbe,pc.GSProbe)):

                raise TypeError(f"passed probe class is invalid ({cls.__name__})")

            cls.__init__(self,*a,*kw)

            self.offset=LayoutDefault.TwoPortProbeoffset

        def draw(self):

            cell=Device(name=self.name)

            probe_cell=super().draw()

            p1=cell.add_ref(probe_cell,alias='Port1')

            p2=cell.add_ref(probe_cell,alias='Port2')

            p2.rotate(
                center=(p1.x,p1.ymax),
                angle=180)

            p2.move(destination=self.offset.coord)

            for n,p in p1.ports.items():

                cell.add_port(port=p,name=n+'_1')

            for n,p in p2.ports.items():

                if 'left' in n:

                    cell.add_port(port=p,name=n.replace('left','right')+'_2')

                else:

                    if 'right' in n:

                        cell.add_port(port=p,name=n.replace('right','left')+'_2')

                    else:

                        cell.add_port(port=p,name=n+'_2')

            return cell

    TwoPort.__name__=f"Two Port {cls.__name__}"

    return TwoPort

def addTwoPortProbe(cls,probe=makeTwoPortProbe(pc.GSGProbe)):

    class TwoPortProbed(addOnePortProbe(cls,probe)):

        def __init__(self,*a,**kw):

            super().__init__(*a,**kw)

        def draw(self):

            device_cell=cls.draw(self)

            probe_cell=self.probe.draw()

            cell=Device(name=self.name)

            cell.add_ref(device_cell, alias=self.name+"Device")

            probe_ref=cell.add_ref(probe_cell, alias=self.name+"Probe")

            self._move_probe_ref(device_cell,probe_ref)

            self._setup_routings(device_cell,probe_ref)

            probe_routing_cell=self._draw_probe_routing()

            cell.add_ref(probe_routing_cell, alias=self.name+"ProbeRouting")

            return cell

        def _draw_probe_routing(self):

            if isinstance(self.probe,pc.GSGProbe):

                routing_cell=Device()

                routing_cell<<self.gndlefttrace.draw()

                routing_cell<<self.gndrighttrace.draw()

                routing_cell<<self.sig1trace.draw()

                routing_cell<<self.sig2trace.draw()

                return routing_cell

            else :

                raise ValueError("To be implemented")

        def _setup_routings(self,device_cell,probe_cell):

            import pdb; pdb.set_trace()

            top_port=[p for p in device_cell.port if 'top' in p.name]

            bottom_port=[p for p in device_cell.port if 'bottom' in p.name]

            top_port_midpoint=pt._get_centroid(top_port)

            bottom_port_midpoint=pt._get_centroid(bottom_port)

            self.probe.offset=pt.Point(
                (top_port_midpoint.x-bottom_port_midpoint.x),
                (top_port_midpoint.y-bottom_port_midpoint.y)+
                2*self.probe_dut_distance.y)

            bbox=super()._bbox_mod(device_cell.bbox)

            if isinstance(self.probe,pc.GSGProbe):

                #ground routing setup
                for index,groundroute in enumerate([self.gndlefttrace,self.gndrighttrace]):

                    groundroute.layer=self.probe.layer

                    groundroute.clearance=bbox

                    groundroute.trace_width=self.gnd_routing_width

                    if index==0:

                        groundroute.side='left'

                        groundroute.source=(probe_cell.ports['gnd_left_1'],)

                        groundroute.destination=(probe_cell.ports['gnd_left_2'],)

                    elif index==1:

                        groundroute.side='right'

                        groundroute.source=(probe_cell.ports['gnd_right_1'],)

                        groundroute.destination=(probe_cell.ports['gnd_right_2'],)

                #signal routing
                for index,sigroute in enumerate([self.sig1trace,self.sig2trace]):

                    sigroute.side='auto'

                    if index==0:

                        sigroute.source=(probe_cell.ports['sig_1'],)

                        dest_port=[]

                        for port_name,cell_port in probe_cell.ports.items():

                            if 'bottom' in port_name:

                                dest_port.append(cell_port)

                        sigroute.source=(probe_cell.ports['sig_1'],)

                        sigroute.destination=tuple(dest_port)

                        sigroute.trace_width=device_cell.ports['bottom'].width

                    elif index==1:

                        sigroute.source=(probe_cell.ports['sig_2'],)

                        dest_port=[]

                        for port_name,cell_port in probe_cell.ports.items():

                            if 'top' in port_name:

                                dest_port.append(cell_port)

                        sigroute.source=(probe_cell.ports['sig_2'],)

                        sigroute.destination=tuple(dest_port)

                        sigroute.trace_width=device_cell.ports['top'].width

                    sigroute.layer=self.probe.layer

                    sigroute.clearance=bbox

            elif isinstance(self.probe,pc.GSProbe):

                raise ValueError("OnePortProbed with GSprobe to be implemented ")

            else:

                raise ValueError("OnePortProbed without GSG/GSprobe to be implemented ")

        def _move_probe_ref(self,device_cell,probe_ref):

            probe_dut_distance=self.probe_dut_distance

            bottom_port=device_cell.ports['bottom']

            top_port=probe_ref.ports['sig_1']

            probe_ref.connect(top_port,
                destination=bottom_port,
                overlap=-probe_dut_distance.y)

        def get_components(self):

            supercomp=copy(super().get_components())

            supercomp.pop("SigTrace")

            supercomp.update({
                "Sig1Trace":pc.ParasiticAwareMultiRouting,
                "Sig2Trace":pc.ParasiticAwareMultiRouting})

            return supercomp

    TwoPortProbed.__name__=f"TwoPortProbed {cls.__name__} with {probe.__name__}"

    return TwoPortProbed

# Device decorator

def add_compass(device : Device) -> Device:
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

def draw_array(
    cell : Device,
    x : int, y : int,
    row_spacing : float = 0 ,
    column_spacing : float = 0 ) -> Device:
    ''' returns a spaced matrix of identical cells, including ports in the output cell.

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

    new_cell=pg.Device(cell.name+"array")

    cell_size=pt.Point(cell.size)+pt.Point(column_spacing,row_spacing)

    cellmat=[]

    ports=[]

    for j in range(y):

        cellvec=[]

        for i in range(x):

            cellvec.append(new_cell.add_ref(cell,alias=cell.name+'_'+str(i)+'_'+str(j)))

            cellvec[i].move(
                destination=(pt.Point(cell_size.x*i,cell_size.y*j)).coord)

            for p in cellvec[i].ports.values():

                ports.append(Port(name=p.name+'_'+str(i)+'_'+str(j),\
                    midpoint=p.midpoint,\
                    width=p.width,\
                    orientation=p.orientation))

        cellmat.append(cellvec)

    for p in ports:

        new_cell.add_port(p)
    #
    # for cellvec in cellmat:
    #
    #     for dr in cellvec:
    #
    #         new_cell.absorb(dr)

    return new_cell

def connect_ports(cell,tags='top',conn_dist=pt.Point(0,100)):
    ''' connects all the ports in the cell with name matching a tag.

    Parameters:
    -----------
        cell : Device

        tags: tuple of str

        conn_dist: pt.Point
            offset from port location.
    '''

    if isinstance(tags,str):

        tags=tuple([tags])

    import pirel.pcells as pc

    connector=pc.MultiRouting()

    for tag in tags:

        if 'top' in tag:

            top_ports=[]

            for name,port in cell.ports.items():

                if tag in name:

                    top_ports.append(port)

            top_conn=Port('top')

            top_conn.width=top_ports[0].width

            top_conn.midpoint=(pt.Point(cell.x,cell.ymax)+conn_dist).coord

            top_conn.orientation=270

            connector.source=tuple([top_conn])

            connector.destination=tuple(top_ports)

            connector.trace_width=top_ports[0].width

            connector.clearance=tuple(tuple(_) for _ in cell.bbox.tolist())

            tracecell=connector.draw()

            top_trace_ref=cell.add_ref(tracecell,alias='TopTrace')

            top_conn.orientation=90

            cell.add_port(top_conn)

        if 'bottom' in tag:

            bottom_conn=Port('bottom')

            bottom_ports=[]

            for name,port in cell.ports.items():

                if tag in name:

                    bottom_ports.append(port)

            bottom_conn.width=bottom_ports[0].width

            bottom_conn.midpoint=(pt.Point(cell.x,cell.ymin)-conn_dist).coord

            bottom_conn.orientation=90

            connector.source=tuple([bottom_conn])

            connector.destination=tuple(bottom_ports)

            connector.trace_width=bottom_ports[0].width

            connector.clearance=tuple(tuple(_) for _ in cell.bbox.tolist())

            tracecell=connector.draw()

            bottom_trace_ref=cell.add_ref(tracecell,alias='BottomTrace')

            bottom_conn.orientation=270

            cell.add_port(bottom_conn)

def add_pads(cell,pad,tags='top'):
    ''' add pad designs to a cell, connecting it to selected ports.

    Parameters:
    -----------
        cell : Device

        pad : pt.LayoutPart

        tags : iterable of str
            used to find ports
    '''

    import pdb; pdb.set_trace()

    if isinstance(tags,str):

        tags=tuple([tags])

    for tag in tags:

        for name,port in cell.ports.items():

            if tag in name:

                pad.port=port

                pad_ref=cell.add_ref(pad.draw())

                pad_ref.connect('conn',destination=port)

def add_vias(cell : Device, bbox, via : pt.LayoutPart, spacing : float = 0,tolerance: float = 0):

    ''' adds via pattern to cell with constraints.

    Parameters:
    -----------

    cell : Device
        where the vias will be located

    bbox : iterable
        x,y coordinates of box ll and ur to define vias patterns size

    via : pt.LayoutPart

    spacing : float

    tolerance : float (default 0)
        if not 0, used to determine via distance from target object border

    Returns:
    --------
    cell_out : Device
    '''

    bbox_cell=pg.bbox(bbox)

    nvias_x=int(np.floor(bbox_cell.xsize/(via.size+spacing)))

    nvias_y=int(np.floor(bbox_cell.ysize/(via.size+spacing)))

    if nvias_x==0 or nvias_y==0:

        raise ValueError("Via is too large for bbox !")

    via_cell=draw_array(via.draw(),
        nvias_x,nvias_y,
        row_spacing=spacing,
        column_spacing=spacing)

    via_cell.move(
        origin=(via_cell.x,via_cell.y),
        destination=(bbox_cell.x,bbox_cell.y))

    tbr=[]

    for elem in via_cell.references:

        if not pt.is_cell_within(elem,cell,tolerance):

            tbr.append(elem)

    via_cell.remove(tbr)

    cell.add_ref(via_cell,alias="Vias")

    # return cell_out

def attach_taper(cell : Device , port : Port , length : float , \
    width2 : float, layer=LayoutDefault.layerTop) :

    t=pg.taper(length=length,width1=port.width,width2=width2,layer=layer)

    t_ref=cell.add_ref(t)

    t_ref.connect(1,destination=port)

    new_port=t_ref.ports[2]

    new_port.name=port.name

    cell.absorb(t_ref)

    cell.remove(port)

    cell.add_port(new_port)

_allmodifiers=(makeScaled,addPad,addPartialEtch,addOnePortProbe,addLargeGround,makeArray,makeFixture,makeNpaths)

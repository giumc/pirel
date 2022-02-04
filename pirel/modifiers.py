import pirel.pcells as pc

import pirel.tools as pt

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray,Device,DeviceReference,Group

from pirel.tools import Point,LayoutDefault,LayoutParamInterface,LayoutPart

import pirel.addOns.standard_parts as ps

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

            pt._copy_ports(d_ref,cell)

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

def addLargeGround(probe):

    ''' legacy decorator to make large ground pads'''

    class LargeGrounded(probe):

        ''' legacy class to make large ground pads.

        Properties:

            ground_size (float).
        '''

        ground_size=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            probe.__init__(self,*args,**kwargs)

            self.ground_size=LayoutDefault.LargePadground_size

        def draw(self):

            oldprobe=probe.draw(self)

            cell=pg.deepcopy(oldprobe)

            groundpad=pt._draw_multilayer(
                'compass',
                layers=self.ground_layer,
                size=(self.ground_size,self.ground_size))

            r=pt._get_corners(groundpad)

            for alias in cell.aliases:

                if 'GroundLX' in alias:

                    dest=cell[alias].ports['N'].endpoints[1]

                    for portname in cell.ports:

                        if alias in portname:

                            cell.remove(cell.ports[portname])

                    cell.remove(cell[alias])

                    groundref=cell.add_ref(groundpad,alias=alias)

                    groundref.move(origin=r.ur.coord,
                    destination=dest)

                    pt._copy_ports(groundref,cell,prefix="GroundLX")

                if 'GroundRX' in alias:

                    dest=cell[alias].ports['N'].endpoints[0]

                    for portname in cell.ports:

                        if alias in portname:

                            cell.remove(cell.ports[portname])

                    cell.remove(cell[alias])

                    groundref=cell.add_ref(groundpad,alias=alias)

                    groundref.move(
                        origin=r.ul.coord,
                        destination=dest)

                    for portname in cell[alias].ports:

                        cell.remove(cell[alias].ports[portname])

                    pt._copy_ports(groundref,cell,prefix="GroundRX")

            return cell

    LargeGrounded.__name__=" ".join([probe.__name__,"w Large Ground"])

    return LargeGrounded

def makeArray(cls,n=2):
    '''class decorator to make arrays of identical pcells.

    Also ports are arrayed.'''
    
    if not isinstance(n,int):

        raise ValueError(" n needs to be integer")

    class Arrayed(cls):

        n_blocks=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.n_blocks=n

        def draw(self):

            unit_cell=cls.draw(self)

            cell=pt.draw_array(
                unit_cell,
                self.n_blocks,1)

            cell.name=self.name

            self._make_internal_ground_connections(cell)

            return cell

        def _make_internal_ground_connections(self,cell):

            lx_ports=pt._find_ports(cell,'GroundLX',depth=0)

            rx_ports=pt._find_ports(cell,'GroundRX',depth=0)

            if len(lx_ports)<=1 or len(rx_ports)<=1:

                return

            else:

                lx_ports.remove(lx_ports[0])

                rx_ports.remove(rx_ports[-1])

            polyconn=pc.PolyRouting()

            polyconn.layer=(self.plate_layer,)

            for l,r in zip(lx_ports,rx_ports):

                polyconn.source=l
                polyconn.destination=r

                cell.add(polyconn.draw())
                cell.remove(cell.ports[l.name])
                cell.remove(cell.ports[r.name])

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

        @property
        def active_area(self):

            active_area=super().active_area

            return pt.Point(active_area.x*self.n_blocks,active_area.y)

        def export_all(self):

            df=super().export_all()

            df["SingleDeviceResistance"]=super().resistance_squares

            return df

    Arrayed.__name__= " ".join([f"{n} array of",cls.__name__])

    return Arrayed

def addPassivation(cls,
    margin=LayoutDefault.PassivationMargin,
    scale=LayoutDefault.PassivationScale,
    layer=LayoutDefault.PassivationLayer):

    class Passivated(cls):

        passivation_margin=LayoutParamInterface()
        passivation_scale=LayoutParamInterface()
        passivation_layer=LayoutParamInterface()

        def __init__(self,*a,**kw):

            cls.__init__(self,*a,**kw)
            self.passivation_margin=margin
            self.passivation_scale=scale
            self.passivation_layer=layer

        def draw(self):

            supercell=cls.draw(self)

            cell=pt.Device(self.name)

            master_ref=cell.add_ref(supercell,alias='Device')

            add_passivation(cell,
                self.passivation_margin,
                self.passivation_scale,
                self.passivation_layer)

            r=pt._get_corners(cell)

            if issubclass(cls,pc.SMD):

                bottom_port=Port(
                    name='S_1',
                    width=self.size.x,
                    orientation=270,
                    midpoint=r.s.coord)

                top_port=Port(
                    name='N_2',
                    width=self.size.x,
                    orientation=90,
                    midpoint=r.n.coord)

                cell.add_port(top_port)
                cell.add_port(bottom_port)

                cell.add(pt._make_poly_connection(
                    bottom_port,
                    master_ref.ports['S_1'],
                    layer=self.layer))

                cell.add(pt._make_poly_connection(
                    top_port,
                    master_ref.ports['N_2'],
                    layer=self.layer))

            else:

                pt._copy_ports(supercell,cell)

            return cell

    Passivated.__name__="Passivated "+cls.__name__

    return Passivated

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

            if style=='open':

                pt._remove_alias(cell,'IDT')

            if style=='short':

                for subcell in cell.get_dependencies(recursive=True):

                    if "IDT" in subcell.name:

                        subcell.remove_polygons(lambda x,y,z : y==self.idt.layer)

                        trace_cell=pc.PolyRouting()

                        trace_cell.source=subcell.ports['top']

                        trace_cell.destination=subcell.ports['bottom']

                        trace_cell.layer=(self.idt.layer,)

                        subcell.add(trace_cell.draw())

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

def makeTwoPortProbe(cls):

    class TwoPort(cls):

        offset=LayoutParamInterface()

        def __init__(self,*a,**kw):

            if not issubclass(cls,(pc.GSGProbe,pc.GSProbe)):

                raise TypeError(f"passed probe class is invalid ({cls.__name__})")

            cls.__init__(self,*a,*kw)

            self.offset=LayoutDefault.TwoPortProbeoffset

        def draw(self):

            def mirror_label(str):

                if 'N_' in str:

                    return str.replace('N_','S_')

                if 'E_' in str:

                    return str.replace('E_','W_')

                if 'S_' in str:

                    return str.replace('S_','N_')

                if 'W_' in str:

                    return str.replace('W_','E_')

                return str

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

                if 'LX' in n:

                    cell.add_port(port=p,name=mirror_label(n+'_2').replace('LX','RX'))

                else:

                    if 'RX' in n:

                        cell.add_port(port=p,name=mirror_label(n+'_2').replace('RX','LX'))

                    else:

                        cell.add_port(port=p,name=mirror_label(n+'_2'))

            return cell

    TwoPort.__name__=f"Two Port {cls.__name__}"

    return TwoPort

def addOnePortProbe(cls,probe=pc.GSGProbe):
    ''' adds a one port probe to existing LayoutClass.

    Parameters:
    -----------
        cls : pt.LayoutPart
            the layout drawn with this LayoutPart needs to have
            a 'bottom' and 'top' port.

        probe: pt.LayoutPart
            currently working only on pc.GSGProbe.
    '''

    class OnePortProbed(cls):
        ''' LayoutPart decorated with a one port probe.

        Parameters:
        -----------
            ground_conn_style : ('straight','side')

            gnd_routing_width: float.

        '''

        gnd_routing_width=LayoutParamInterface()

        def __init__(self,*args,**kwargs):

            cls.__init__(self,*args,**kwargs)

            self.gnd_routing_width=100.0

        def draw(self):

            self._set_relations()

            device_cell=cls.draw(self)

            probe_cell=self.probe.draw()

            cell=Device(name=self.name)

            cell.add_ref(device_cell, alias="Device")

            self._add_signal_connection(cell,'bottom')

            probe_ref=cell.add_ref(probe_cell, alias="Probe")

            self._move_probe_ref(cell)

            self._setup_signal_routing(cell)

            cell.absorb(cell<<self._draw_signal_routing())

            try:

                self._setup_ground_routing(
                    cell,
                    'straight')

                routing_cell=self._draw_ground_routing()

            except:

                self._setup_ground_routing(
                    cell,
                    'side')

                routing_cell=self._draw_ground_routing()

            _add_default_ground_vias(self,routing_cell)

            cell.add_ref(routing_cell,alias=self.name+"GroundTrace")

            return cell

        def _add_signal_connection(self,cell,tag):

            device_cell=cell["Device"]

            ports=pt._find_ports(device_cell,tag,depth=0)

            if len(ports)>1:

                distance=self.probe_dut_distance.y-self.probe_conn_distance.y

                port_mid=pt._get_centroid_ports(ports)

                if distance-port_mid.width>0:

                    sigtrace=connect_ports(
                        device_cell,
                        tag=tag,
                        layers=self.probe.sig_layer,
                        distance=distance-port_mid.width,
                        metal_width=port_mid.width)

                else:

                    sigtrace=connect_ports(
                        device_cell,
                        tag=tag,
                        layers=self.probe.sig_layer,
                        distance=0,
                        metal_width=distance)

                _add_default_ground_vias(self,sigtrace)

                cell.absorb(cell<<sigtrace)

                sigtrace.ports[tag].width=self.probe.size.x

                pt._copy_ports(sigtrace,cell)

            else:

                cell.add_port(port=device_cell.ports[tag])

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
                    "SigTrace":pc.Routing,
                    "GndLeftTrace":pc.MultiRouting,
                    "GndRightTrace":pc.MultiRouting,
                    "GndVia":pc.Via})

            else:

                raise ValueError("To be implemented")

            return supercomp

        @property
        def probe_resistance_squares(self):

            return 0

        @property
        def probe_dut_distance(self):

            base_dist=self.idt.probe_distance

            if hasattr(self,'pad'):

                base_dist=pt.Point(base_dist.x,self.pad.size+self.pad.distance+base_dist.y)

            if hasattr(self.probe,'pad'):

                base_dist=pt.Point(base_dist.x,self.probe.pad.size+self.probe.pad.distance+base_dist.y)

            return base_dist

        @property
        def probe_conn_distance(self):

            tot_distance=self.probe_dut_distance

            return pt.Point(tot_distance.x,tot_distance.y*3/4)

        def _move_probe_ref(self,cell):

            device_ref=cell["Device"]

            probe_ref=cell["Probe"]

            bottom_ports=pt._find_ports(cell,'bottom',depth=0,exact=True)

            try:

                probe_port=probe_ref.ports['SigN']

            except:

                probe_port=probe_ref.ports['SigN_1']

            top_ports=pt._find_ports(device_ref,'top')

            if len(top_ports)>1:

                probe_ref.connect(
                    port=probe_port,
                    destination=bottom_ports[0],
                    overlap=-self.probe_conn_distance.y)

            else:

                probe_ref.connect(
                    port=probe_port,
                    destination=bottom_ports[0],
                    overlap=-self.probe_dut_distance.y)

        def _setup_ground_routing(self,cell,label):

            device_ref=cell["Device"]

            probe_ref=cell["Probe"]

            bbox=super()._bbox_mod(device_ref.bbox)

            if isinstance(self.probe,pc.GSGProbe):

                for index,groundroute in enumerate([self.gndlefttrace,self.gndrighttrace]):

                    groundroute.layer=self.probe.ground_layer

                    groundroute.clearance=bbox

                    groundroute.set_auto_overhang(True)

                    groundroute.trace_width=self.gnd_routing_width

                    if index==0:

                        groundroute.side='left'

                        if label=='straight':

                            groundroute.source=(probe_ref.ports['GroundLXN'],)

                        elif label=='side':

                            groundroute.source=(probe_ref.ports['GroundLXW'],)

                    elif index==1:

                        groundroute.side='right'

                        if label=='straight':

                            groundroute.source=(probe_ref.ports['GroundRXN'],)

                        elif label=='side':

                            groundroute.source=(probe_ref.ports['GroundRXE'],)

                    dest_ports=pt._find_ports(device_ref,'top')

                    groundroute.destination=tuple(dest_ports)

            elif isinstance(self.probe,pc.GSProbe):

                raise ValueError("OnePortProbed with GSprobe to be implemented ")

            else:

                raise ValueError("OnePortProbed without GSG/GSprobe to be implemented ")

        def _draw_ground_routing(self):

            if isinstance(self.probe,pc.GSGProbe):

                routing_cell=Device()

                routing_cell.absorb(routing_cell<<self.gndlefttrace.draw())

                routing_cell.absorb(routing_cell<<self.gndrighttrace.draw())

                return pt.join(routing_cell)

            else :

                raise ValueError("To be implemented")

        def _setup_signal_routing(self,cell):

            sig_trace=self.sigtrace

            sig_trace.layer=self.probe.sig_layer

            sig_trace.source=cell["Probe"].ports["SigN"]

            sig_trace.destination=cell.ports["bottom"]

            sig_trace.trace_width=self._calc_sig_routing_width(sig_trace.source,sig_trace.destination)

            sig_trace.set_auto_overhang(True)

        def _calc_sig_routing_width(self,pad_port,device_port):

            if device_port.width>pad_port.width:

                return device_port.width

            else:

                return None

        def _draw_signal_routing(self):

            return self.sigtrace.draw()

        def get_params(self):

            df=super().get_params()

            modkeys=[*df.keys()]

            pt.pop_all_match(modkeys,"SigTrace")

            pt.pop_all_match(modkeys,"GndLeftTrace")

            pt.pop_all_match(modkeys,"GndRightTrace")

            return {k: df[k] for k in modkeys }

    OnePortProbed.__name__=" ".join([cls.__name__,"w Probe"])

    return OnePortProbed

def addTwoPortProbe(cls,probe=makeTwoPortProbe(pc.GSGProbe)):

    class TwoPortProbed(addOnePortProbe(cls,probe)):

        def __init__(self,*a,**kw):

            super().__init__(*a,**kw)

        def draw(self):

            device_cell=cls.draw(self)

            cell=Device(name=self.name)

            device_ref=cell.add_ref(device_cell, alias="Device")

            self._setup_probe(device_ref)

            probe_cell=self.probe.draw()

            probe_ref=cell.add_ref(probe_cell, alias="Probe")

            for tag in ('top','bottom'):

                self._add_signal_connection(cell,tag)

            self._move_probe_ref(cell)

            self._setup_ground_routing(device_ref,probe_ref,'side')

            routing_cell=self._draw_ground_routing()

            self._setup_signal_routing(cell)

            routing_cell.add(self._draw_device_grounds(device_ref,probe_ref,'side'))

            routing_cell.add(self._draw_signal_routing())

            _add_default_ground_vias(self,routing_cell)

            cell.add_ref(routing_cell,alias="GroundTrace")

            return cell

        def _setup_probe(self,device_cell):

            top_ports=[pt.Point(p.midpoint) for p in pt._find_ports(device_cell,'top',depth=0)]

            bottom_ports=[pt.Point(p.midpoint) for p in pt._find_ports(device_cell,'bottom',depth=0)]

            top_port_midpoint=pt._get_centroid(*top_ports)

            bottom_port_midpoint=pt._get_centroid(*bottom_ports)

            self.probe.offset=pt.Point(
                (top_port_midpoint.x-bottom_port_midpoint.x),
                (top_port_midpoint.y-bottom_port_midpoint.y)+2*self.probe_dut_distance.y)

        def _draw_ground_routing(self):

            if isinstance(self.probe,pc.GSGProbe):

                routing_cell=Device()

                routing_cell<<self.gndlefttrace.draw()

                routing_cell<<self.gndrighttrace.draw()

                return routing_cell

            else :

                raise ValueError("To be implemented")

        @staticmethod
        def get_components():

            supercomp=copy(cls.get_components())

            if issubclass(probe,pc.GSGProbe):

                supercomp.update({
                    "Probe":probe,
                    "Sig1Trace":pc.Routing,
                    "Sig2Trace":pc.Routing,
                    "GndLeftTrace":pc.MultiRouting,
                    "GndRightTrace":pc.MultiRouting,
                    "GndVia":pc.Via})

            else:

                raise ValueError("To be implemented")

            return supercomp

        def get_params(self):

            df=super().get_params()

            modkeys=[*df.keys()]

            pt.pop_all_match(modkeys,"Sig1Trace")

            pt.pop_all_match(modkeys,"Sig2Trace")

            pt.pop_all_match(modkeys,"GndLeftTrace")

            pt.pop_all_match(modkeys,"GndRightTrace")

            return {k: df[k] for k in modkeys }

        def _draw_device_grounds(self,device_cell,probe_cell,label):

            output_cell=Device()

            lx_device_ports=[]

            rx_device_ports=[]

            gnd_ports=pt._find_ports(device_cell,'Ground',depth=0)

            if not gnd_ports:

                return output_cell

            for p in gnd_ports:

                p_adj=Port(
                    name=p.name,
                    midpoint=p.midpoint,
                    width=probe_cell['Port1'].size[1],
                    orientation=p.orientation)

                if "LX" in p.name:

                    lx_device_ports.append(p_adj)

                elif "RX" in p.name:

                    rx_device_ports.append(p_adj)

            r=pc.MultiRouting()

            r.layer=self.gndlefttrace.layer

            r.clearance=pt._bbox_to_tuple(self._bbox_mod(device_cell.bbox))

            r.trace_width=self.gnd_routing_width

            ## left connections

            if label=='side':

                r.source=tuple(pt._find_ports(probe_cell,'GroundLXW',depth=0))

            elif label=='straight':

                r.source=(probe_cell.ports['GroundLXN_1'],)

            r.destination=tuple(lx_device_ports)

            r.side='left'

            output_cell.absorb(output_cell<<r.draw())

            ## right connections

            if label=='side':

                r.source=tuple(pt._find_ports(probe_cell,'GroundRXE',depth=0))

            elif label=='straight':

                r.source=(probe_cell.ports['GroundRXN_1'],)

            r.destination=tuple(rx_device_ports)

            r.side='right'

            output_cell.absorb(output_cell<<r.draw())

            return output_cell

        def _setup_ground_routing(self,device_cell,probe_cell,label):

            bbox=super()._bbox_mod(device_cell.bbox)

            if isinstance(self.probe,pc.GSGProbe):

                #ground routing setup
                for index,groundroute in enumerate([self.gndlefttrace,self.gndrighttrace]):

                    groundroute.layer=self.probe.ground_layer

                    groundroute.clearance=bbox

                    groundroute.trace_width=self.gnd_routing_width

                    if index==0:

                        groundroute.side='left'

                        if label=='straight':

                            groundroute.source=(probe_cell.ports['GroundLXN_1'],)

                            groundroute.destination=(probe_cell.ports['GroundLXS_2'],)

                        elif label=='side':

                            groundroute.source=(probe_cell.ports['GroundLXW_1'],)

                            groundroute.destination=(probe_cell.ports['GroundLXW_2'],)

                    elif index==1:

                        groundroute.side='right'

                        if label=='straight':

                            groundroute.source=(probe_cell.ports['GroundRXN_1'],)

                            groundroute.destination=(probe_cell.ports['GroundRXS_2'],)

                        elif label=='side':

                            groundroute.source=(probe_cell.ports['GroundRXE_1'],)

                            groundroute.destination=(probe_cell.ports['GroundRXE_2'],)

                    # groundroute.set_auto_overhang(True)

            elif isinstance(self.probe,pc.GSProbe):

                raise ValueError("OnePortProbed with GSprobe to be implemented ")

            else:

                raise ValueError("OnePortProbed without GSG/GSprobe to be implemented ")

        def _setup_signal_routing(self,cell):

            probe=cell["Probe"]

            for sig_trace in (self.sig1trace,self.sig2trace):

                sig_trace.layer=self.probe.sig_layer

                sig_trace.set_auto_overhang(True)

            self.sig1trace.source=probe.ports["SigN_1"]

            self.sig1trace.destination=cell.ports["bottom"]

            self.sig1trace.trace_width=self._calc_sig_routing_width(self.sig1trace.source,self.sig1trace.destination)

            self.sig2trace.source=probe.ports["SigS_2"]

            self.sig2trace.destination=cell.ports["top"]

            self.sig2trace.trace_width=self._calc_sig_routing_width(self.sig2trace.source,self.sig2trace.destination)

        def _draw_signal_routing(self):

            cell=Device()

            cell.add(self.sig1trace.draw())

            cell.add(self.sig2trace.draw())

            return cell

    TwoPortProbed.__name__=f"TwoPortProbed {cls.__name__} with {probe.__name__}"

    return TwoPortProbed

def addGroundVias(cls):

    class withGroundVia(cls):

        def draw(self):

            cell=pg.deepcopy(cls.draw(self))

            _add_default_ground_vias(self,cell)

            return cell

        @staticmethod
        def get_components():

            supercomp=copy(cls.get_components())

            supercomp.update({"GndVia":pc.Via})

            return supercomp

    return withGroundVia

def connectPorts(cls,tags,layers):

    if isinstance(tags,str):

        tags=[tag]

    class connectedPorts(cls):

        connector_distance=LayoutParamInterface()

        def __init__(self,*a,**kw):

            super().__init__(*a,**kw)

            self.connector_distance=pt.Point(0,100)

        def draw(self):

            cell=Device(self.name)

            supercell=super().draw()

            cell<<supercell

            for t in tags:

                connector=connect_ports(
                    supercell,
                    t,
                    layers=layers,
                    distance=self.connector_distance.y)

                cell<<connector

                pt._copy_ports(connector,cell)

            return cell

    connectPorts.__name__=f"{cls.__name__} w connected Ports"

    return connectedPorts
# Device decorator

def connect_ports(
    cell : Device,
    tag : str ='top',
    layers : tuple = (LayoutDefault.layerTop,),
    distance : float = 10.0,
    metal_width: float = None):
    ''' connects all the ports in the cell with name matching a tag.

    Parameters:
    -----------
        cell : Device

        tag: str

        conn_dist: pt.Point
            offset from port location

        layer : tuple.


    Returns:
    ----------

        cell : Device
            contains routings and connection port

    '''

    import pirel.pcells as pc

    ports=pt._find_ports(cell,tag,depth=0)

    ports.sort(key=lambda x: x.midpoint[0])

    ports_centroid=pt._get_centroid_ports(ports)

    if len(ports)==1:

        raise ValueError("pm.connect_ports() : len(ports) must be >1 ")

    if metal_width is None:

        metal_width=ports_centroid.width

    port_mid_norm=pt.Point(ports_centroid.normal[1])-pt.Point(ports_centroid.normal[0])

    midpoint_projected=Point(ports_centroid.midpoint)+port_mid_norm*(distance+metal_width)

    pad_side=ports_centroid.width

    new_port=Port(
        name=tag,
        orientation=ports_centroid.orientation,
        width=ports_centroid.width,
        midpoint=midpoint_projected.coord)

    output_cell=Device()

    for p in ports:

        straight_conn=output_cell<<pt._draw_multilayer(
            'compass',
            layers,size=(p.width,abs(midpoint_projected.y-p.midpoint[1])))

        straight_conn.connect("S",p)

    cross_conn=output_cell<<pt._draw_multilayer(
        'compass',
        layers,size=(output_cell.xsize,metal_width))

    cross_conn.connect('S',new_port,overlap=metal_width)

    output=pt.join(output_cell)

    output.add_port(new_port)

    return output

def add_pads(cell,pad,tag='top',exact=False):
    ''' add pad designs to a cell, connecting it to selected ports.

    Parameters:
    -----------
        cell : Device

        pad : pt.LayoutPart

        tags : str (or iterable of str)
            used to find ports
    '''
    if not isinstance(tag,str):

        ports=[]

        for t in tag:

            ports.extend(pt._find_ports(cell,t,depth=0,exact=exact))

    else:

        ports=pt._find_ports(cell,tag,depth=0,exact=exact)

    pad_cell=Device()

    for port in ports:

        pad.port=port

        pad_ref=pad_cell.add_ref(pad.draw())

        pad_ref.connect('conn',destination=port)

    cell.add_ref(pad_cell,alias="Pad")

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

        return

    via_cell=pt.draw_array(via.draw(),
        nvias_x,nvias_y,
        row_spacing=spacing,
        column_spacing=spacing)

    via_cell.move(
        origin=(via_cell.x,via_cell.y),
        destination=(bbox_cell.x,bbox_cell.y))

    tbr=[]

    for elem in via_cell.references:

        if not pt.is_cell_inside(elem,cell,tolerance):

            tbr.append(elem)

    via_cell.remove(tbr)

    cell.absorb(cell.add_ref(via_cell,alias="Vias"))

    # return cell_out

def add_passivation(cell,margin,scale,layer):

    rect=pg.rectangle(
        size=(
            cell.xsize*scale.x,
            cell.ysize*scale.y))

    margin_rect=pg.rectangle(
        size=(margin.x*cell.xsize,
        margin.y*cell.ysize))

    rect.move(origin=rect.center,
        destination=cell.center)

    margin_rect.move(origin=margin_rect.center,
            destination=cell.center)

    pa=pg.boolean(rect,
        margin_rect,
        operation='xor')

    for l in layer:

            cell.add_polygon(pa.get_polygons(),layer=(l,0))

def _add_default_ground_vias(self,cell):

    if hasattr(self,'gndvia'):

        add_vias(cell,
            cell.bbox,
            self.gndvia,
            spacing=self.gndvia.size*1.25,
            tolerance=self.gndvia.size/2)
#
# _allmodifiers=(
#     makeScaled,addPad,addPartialEtch,
#     addOnePortProbe,addLargeGround,
#     makeArray,makeFixture,makeNpaths)

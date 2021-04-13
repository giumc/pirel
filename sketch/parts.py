
from building_blocks import *

from tools import *

ld=LayoutDefault()

class LFERes(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.layer=ld.IDTlayer

        self.idt=IDT(name='ResIDT')

        self.bus=Bus(name='ResBus')

        self.etchpit=EtchPit(name='ResEtchPit')

        self.anchor=Anchor(name='ResAnchor')

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

        self.anchor.etch_x=self.etchpit.x*2+self.etchpit.active_area.x

        self.anchor.layer=self.layer

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
        cell_out.add_port(Port(name=self.name+"Top",\
        midpoint=(Point().from_iter(ports[1].center)+\
        Point(0,self.anchor.size.y))(),\
        width=self.anchor.size.x,\
        orientation=90))

        cell_out.add_port(Port(name=self.name+"Bottom",\
        midpoint=(Point().from_iter(ports[0].center)-\
        Point(0,self.anchor.size.y))(),\
        width=self.anchor.size.x,\
        orientation=-90))

        del idt_cell,bus_cell,etch_cell,anchor_cell

        self.cell=cell

        return cell_out

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

        # self.idt_bottom=copy(self.idt)
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
        # print_ports(cell)
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

class DUT(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.dut=LFERes(name=self.name+'_DUT')
        self.probe=GSGProbe(name=self.name+'_Probe')
        self.routing_width=ld.DUTrouting_width

    def draw(self):

        dut=self.dut
        probe=self.probe

        device_cell=dut.draw()
        probe_cell=probe.draw()

        cell=Device(name=self.name)

        cell<<device_cell
        probe_ref=cell<<probe_cell

        ports=cell.get_ports()

        probe_ref.connect(ports[2],\
        destination=ports[1],overlap=-self.routing_width*3)

        ports=cell.get_ports()

        dut_port_bottom=ports[1]
        dut_port_top=ports[0]

        bbox=device_cell.bbox

        if isinstance(self.probe,GSGProbe):

            probe_port_lx=ports[3]
            probe_port_center=ports[2]
            probe_port_rx=ports[4]

            routing_lx=self._route(bbox,probe_port_lx,dut_port_top,side='left')
            routing_c=self._route(bbox,probe_port_center,dut_port_bottom)
            routing_rx=self._route(bbox,probe_port_rx,dut_port_top,side='right')
            routing_tot=pg.boolean(routing_lx,routing_rx,'or',layer=probe.layer)

            cell<<routing_tot
            cell<<routing_c

        del probe_cell,device_cell,routing_lx,routing_rx,routing_c,routing_tot

        cell.flatten()
        join(cell)
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

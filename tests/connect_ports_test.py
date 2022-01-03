from pirel.modifiers import connect_ports
from phidl.device_layout import Port,Device
from phidl import quickplot as qp
from phidl import set_quickplot_options

set_quickplot_options(blocking=True)

distance=40
width=20
spacing=60
n=9

d=Device()

for i in range(n):

    d.add_port(
        Port(
            midpoint=(spacing*i,0),
            width=width,
            orientation=90,
            name='top_'+str(i)
        )
    )

connector=connect_ports(d,
    tag='top',
    distance=distance)

d<<connector

for p in connector.get_ports(depth=0):

    d.add_port(connector.ports[p.name])

qp(d)

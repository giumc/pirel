import phidl.geometry as pg
from phidl.device_layout import Device,Port
from phidl import quickplot as qp
import matplotlib.pyplot as plt

r=pg.ring()

d=Device()

d<<r

r.add_port(Port('center',midpoint=(0,0),width=10))

r2=d<<r

r2.move(origin=(0,0),destination=(20,0))

d_super=Device()

d_super<<d

qp(d)

plt.pause(2)

qp(d_super)

plt.pause(2)

print('Ports in subcell',* d.get_ports(),sep='\n')
print('Ports in supercell',* d_super.get_ports(),sep='\n')

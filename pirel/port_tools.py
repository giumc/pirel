from pirel.tools import Point

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray,Device,DeviceReference

import phidl.device_layout as dl

import phidl.path as path

def extend_port(port,width,length,layer):
    '''Create a rectangle extending perpendicularly from the port.

    Attributes:
    ----------
        port : dl.Port

        width : float

        length : float

        layer : int, tuple or set

    Returns:
    -------
        dl.Device.
    '''

    p1=Point(port.midpoint)

    dir=Point(port.normal[1])-Point(port.normal[0])

    p2=p1+dir*length

    p=path.smooth(points=[p1.coord,p2.coord])

    return p.extrude(width=width,layer=layer)

def shift_port(port,dist):
    '''Returns new port with translated midpoint.

    Attributes:
    ----------
        port : dl.Port

        dist : float

    Returns:
        dl.Port.
    '''

    port_mid_norm=Point(port.normal[1])-Point(port.normal[0])

    midpoint_projected=Point(port.midpoint)+port_mid_norm*dist

    new_port=Port(
        name=port.name+'shifted',
        orientation=port.orientation,
        width=port.width,
        midpoint=midpoint_projected.coord)

    return new_port

def copy_ports(source,dest,prefix='',suffix=''):
    ''' Copies port from a cell to another.

    Attributes:
    ----------
        source :dl.Device

        dest : dl.Device

        prefix : string (optional)

        suffix : string (optional)
    '''

    for n,p in source.ports.items():

        dest.add_port(port=p,name=prefix+n+suffix)

def find_ports(cell,tag,depth=None,exact=False):
    ''' Finds ports within cell.

        Supports hierarchy search (through depth parameter), and exact match (trough exact parameter).

        Attributes:
        ----------
            cell : dl.Device

            tag: string

            depth : int (or None, default None)

            exact : boolean (default False)

        Returns:
            list of dl.Port.
        '''

    output=[]

    if isinstance(cell,Device):

        for port in cell.get_ports(depth=depth):

            if exact:

                if port.name==tag:

                    output.append(port)

            else:

                if tag in port.name:

                    output.append(port)

        return output

    elif isinstance(cell,DeviceReference):

        for port in cell.ports.values():

            if exact:

                if port.name==tag:

                    output.append(port)

            else:

                if tag in port.name:

                    output.append(port)

        return output

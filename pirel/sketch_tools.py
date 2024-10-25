from pirel.tools import Point

from abc import ABC, abstractmethod

import numpy as np

from pandas import Series,DataFrame

from phidl import set_quickplot_options

from phidl import quickplot as qp

import warnings, re, pathlib, gdspy, pdb, functools, inspect

import phidl.geometry as pg

from phidl.device_layout import Port,CellArray,Device,DeviceReference

import phidl.device_layout as dl

import phidl.path as path

def join(device : Device) -> Device:
    ''' returns a copy of device with all polygons joined.

    Parameters
    ----------
    device : phidl.Device.
    '''


    out_cell=pg.union(device,by_layer=True, precision=0.001,join_first=False)

    return out_cell

def get_corners(device : Device) :
    ''' get corners of a device.

    Parameters
    ---------
    device : phidl.Device

    Returns:
    ll : pt.Point
        lower left

    lr : pt.Point
        lower right

    ul : pt.Point
        upper left

    ur : pt.Point

    c : pt.Point

    n : pt.point

    s : pt.point

    w : pt.Point

    e : pt.Point.
    '''
    bbox=device.bbox
    ll=Point(bbox[0,0],bbox[0,1])
    lr=Point(bbox[1,0],bbox[0,1])
    ul=Point(bbox[0,0],bbox[1,1])
    ur=Point(bbox[1,0],bbox[1,1])
    n=Point(device.center[0],bbox[1,1])
    s=Point(device.center[0],bbox[0,1])
    w=Point(bbox[0,0],device.center[1])
    e=Point(bbox[1,0],device.center[1])
    c=Point(device.center)

    class ReferencePoints():
        pass

    r=ReferencePoints()
    r.ll=ll
    r.lr=lr
    r.ul=ul
    r.ur=ur
    r.c=c
    r.n=n
    r.s=s
    r.w=w
    r.e=e
    return r

def check(device : Device, joined=False, blocking=True,gds=False,*a,**kw):
    ''' Shows the device layout.

        If run by terminal, blocks script until window is closed.

        Parameters
        ----------
            device : phidl.Device

            joined : boolean (optional, default False)
                if true, returns a flattened/joined version of device

            gds : boolean
                if true, view in gdspy viewer

    '''
    set_quickplot_options(blocking=blocking,*a,**kw)

    if joined:

        cell=join(device)

    else:

        cell=device

    if gds:

        lib=gdspy.GdsLibrary()

        gcell=lib.new_cell("Output")

        gcell.add(cell)

        gdspy.LayoutViewer(lib)

    else:

        qp(cell)

def generate_gds_from_image(path,**kwargs):

    import nazca as nd # type: ignore

    if isinstance(path,pathlib.Path):

        path=str(path.absolute())

    else:

        path=pathlib.Path(path)

    cell=nd.image(path,**kwargs).put()

    path=path.parent/(path.stem+".gds")

    nd.export_gds(filename=str(path.absolute()))

    return path

def import_gds(path,cellname=None,flatten=True,**kwargs):

    if isinstance(path,str):

        path=pathlib.Path(path)

    cell=pg.import_gds(str(path.absolute()))

    if flatten==True:
        cell.flatten()

    if cellname is not None:

        cell._internal_name=cellname

    return cell

def get_centroid(*points):

    ''' Calculates centroid of passed points.

    Arguments:
    ---------
        *points : pt.Point

    Returns:
    --------
        pt.Point.
    '''
    x_c=0
    y_c=0

    if isinstance(points, Point):

        return points

    for p in points:

        x_c=x_c+p.x
        y_c=y_c+p.y

    return Point(x_c,y_c)/len(points)

def get_centroid_ports(*ports):
    '''Calculate port with matching orientation and with as input ports, and midpoint at the
        centroid of the input ports midpoint.

    Attributes:
    ----------
        *ports : dl.Port

    Returns:
    -------
        dl.Port.
    '''

    if not ports:

        raise ValueError(f"st.get_centroid_ports(): no ports passed")

    if isinstance(ports,Port):

        return ports

    else:

        ports_centroid=get_centroid(*[Point(x.midpoint) for x in ports])

        ports_width=np.average([x.width for x in ports])

        ports_orientation=np.average([x.orientation for x in ports])

        return Port(
        orientation=ports_orientation,
        width=ports_width,
        midpoint=ports_centroid.coord)

def get_angle(p1,p2):
    '''Calculates angle between two pt.Points'''

    # if not (isinstance(p1,Point) and isinstance(p2,Point)):
    #
    #     import pdb; pdb.set_trace()
    #
    #     raise ValueError(f"{p1} and {p2} have to be pirel Points")

    import numpy as np

    p_diff=p2-p1

    return np.rad2deg(np.arctan2(p_diff.y,p_diff.x) % (2 * np.pi))

def copy_layer(cell,l1,l2):
    ''' Copy each polygon in cell from layer l1 to layer l2.

    Attributes:
    ----------
        cell :dl. Device
        l1: int
        l2: int

    Returns:
        dl.Device.
    '''

    flatcell=join(cell)

    tobecopied=flatcell.get_polygons(byspec=(l1,0))

    cell.add_polygons(tobecopied,l2)

def move_relative_to_cell(
    cell_to_be_moved,
    cell_ref,
    anchor_source='ll',
    anchor_dest='ll',
    offset=(0,0)):
    '''Move cell_to_be_moved relative to cell_ref, by specifying anchors.

        Anchors are specified as described in get_corners().
        Offset is specified as normalized to cell_ref size.

        Attributes:
        ---------
            cell_to_be_moved: dl.Device

            cell_ref:dl.Device

            anchor_source: string

            anchor_dest: string

            offset : tuple.
    '''


    a_origin=get_anchor(anchor_source,cell_to_be_moved)

    a_end=get_anchor(anchor_dest,cell_ref)

    dx=cell_ref.xmax-cell_ref.xmin
    dy=cell_ref.ymax-cell_ref.ymin

    offset=Point(dx*offset[0],dy*offset[1])

    cell_to_be_moved.move(
        origin=a_origin.coord,
        destination=a_end.coord)
    cell_to_be_moved.move(
        destination=offset.coord)

def get_anchor(text,cell):
    '''get a cell anchor.

    Attributes:
    ----------
        text : string
            formatted as described in get_corners()

        cell :dl. Device.

    Returns:
    -------
        pt.Point.
    '''

    r=get_corners(cell)

    return r.__getattribute__(text)

def is_cell_inside(
    cell_test : Device ,
    cell_ref : Device,
    tolerance: float =0):
    ''' Checks whether cell_test is contained in cell_ref.

    Parameters:
    ---------
    cell_test : Device

    cell_ref : Device

    tolerance : float (optional)

    Returns:
        True (if strictly cell_test<cell_ref)
        False (otherwise).

    Note:
        if tolerance is not zero, then function returns True if cell<cell_ref+-tolerance
        in all direction
    '''

    if tolerance==0:

        return _is_cell_inside(cell_test,cell_ref)

    else:

        shifts_set=np.array([[1,1],[-1,-1],[1,-1],[-1,1]])*tolerance

        for shift in shifts_set:

            cell_test.move(destination=shift)

            if not _is_cell_inside(
                cell_test,
                cell_ref):

                cell_test.move(destination=-shift)

                return False

            else:

                cell_test.move(destination=-shift)

        else:

            return True

def _is_cell_inside(cell_test,cell_ref):

    area_pre,area_post=_calculate_pre_post_area(cell_test,cell_ref)

    if round(area_pre,3) >= round(area_post,3)-1e-3:

        return True

    else:

        return False

def is_cell_outside(
    cell_test : Device ,
    cell_ref : Device,
    tolerance: float =0):
    ''' Checks whether cell_test is not overlap with cell_ref.

    Parameters:
    ---------
    cell_test : Device

    cell_ref : Device

    tolerance : float (optional)

    Returns:
        True (if strictly cell_tot>=cell_test+cell_ref)
        False (otherwise).

    Note:
        if tolerance is not zero, then function returns True if cell_tot>=cell_test+cell_ref-tol
        in all direction
    '''

    if tolerance==0:

        return _is_cell_outside(cell_test,cell_ref)

    else:

        shifts_set=np.array([[1,1],[-1,-1],[1,-1],[-1,1]])*tolerance

        for shift in shifts_set:

            cell_test.move(destination=shift)

            if not _is_cell_outside(
                cell_test,
                cell_ref):

                cell_test.move(destination=-shift)

                return False

            else:

                cell_test.move(destination=-shift)

        else:

            return True

def _is_cell_outside(cell_test,cell_ref):

    area_test=cell_test.area()

    area_ref,area_post=_calculate_pre_post_area(cell_test,cell_ref)

    if round(area_post,3)>=round(area_ref+area_test,3)-1e-3:

        return True

    else:

        return False

def _calculate_pre_post_area(cell_test,cell_ref):

    area_pre=cell_ref.area()

    c_flat=pg.union(cell_ref, by_layer=False, layer=100)

    if isinstance(cell_test,Device):

        c_flat.add_ref(cell_test)

    else:

        if isinstance(cell_test,DeviceReference):

            c_flat.add(cell_test)

    area_post=_get_cell_area(c_flat)

    return area_pre,area_post

def _get_cell_area(cell):

    c_flat=pg.union(cell, by_layer=False, layer=100)

    return c_flat.area()

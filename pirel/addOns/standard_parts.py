import pandas as pd

import phidl.geometry as pg

import phidl.device_layout as dl

from phidl.device_layout import Group

import pathlib

import gdspy

import numpy as np

from pirel.tools import *

import pirel.tools as pt

import pirel.pcells as pc

def resistivity_test_cell():

    """Create cell with standard Resisistivity Test

    Returns
    ------

        cell : phidl.Device

    """

    with open(str(pathlib.Path(__file__).parent/'ResistivityTest.gds'), 'rb') as infile:

        cell=pg.import_gds(infile,cellname='TestCell')

        cell=join(cell)

        cell.name='ResistivityTest'

        return cell

def verniers(scale=[1, 0.5, 0.1],layers=[1,2],label='TE',text_size=20,reversed=False):

    """ Create a cell with vernier aligners.

    Parameters
    ----------
        scale : iterable of float (default [1,0.5,0.25])
            each float in list is the offset of a vernier.
            for each of them a vernier will be created in the X-Y axis

        layers : 2-len iterable of int (default [1,2])
            define the two layers for the verniers.

        label : str (default "TE")

            add a label to the set of verniers.

        text_size : float (default)

            label size

        reversed : boolean

            if true, creates a negative alignment mark for the second layer

    Returns
    -------
        cell : phidl.Device.
    """

    cell=dl.Device(name="verniers")

    import numpy

    if not isinstance(scale, numpy.ndarray):

        scale=np.array(scale)

    scale=np.sort(scale)

    xvern=[]

    for dim in scale:

        notch_size=[dim*5, dim*25]
        notch_spacing=dim*10
        num_notches=5
        notch_offset=dim
        row_spacing=0
        layer1=layers[0]
        layer2=layers[1]

        cal=pg.litho_calipers(\
            notch_size,\
            notch_spacing,\
            num_notches,\
            notch_offset,\
            row_spacing,\
            layer1,\
            layer2)

        cal.flatten()

        if reversed:

            tobedel=cal.get_polygons(by_spec=(layer2,0))

            cal=cal.remove_polygons(lambda pts, layer, datatype: layer == layer2)

            replica=dl.Device()

            replica.add(gdspy.PolygonSet(tobedel,layer=layer2))

            frame=dl.Device()

            frame.add(pg.bbox(replica.bbox,layer=layer2))

            frame_ext=dl.Device()

            frame_ext.add(gdspy.PolygonSet(frame.copy('tmp',scale=1.5).get_polygons(),layer=layer2))

            frame_ext.flatten()

            frame_ext.move(origin=frame_ext.center,destination=replica.center)

            new_cal=pg.boolean(replica,frame_ext,'xor',layer=layer2)

            new_cal.rotate(angle=180,center=(cal.xmin+cal.xsize/2,cal.ymin))

            new_cal.move(destination=(0,-notch_size[1]))

            cal<<new_cal

            cal.flatten()

        xvern.append(cal)

    g=dl.Group(xvern)

    g.distribute(direction='y',spacing=scale[-1]*20)
    g.align(alignment='x')
    xcell=dl.Device(name="x")

    for x in xvern:

        xcell<<x

    xcell=join(xcell)

    vern_x=cell<<xcell
    vern_y=cell<<xcell

    vern_y.rotate(angle=-90)
    vern_y.move(origin=(vern_y.xmin,vern_y.y),\
        destination=(vern_x.x+scale[-1]*10,vern_x.ymin-scale[-1]*10))

    cell.absorb(vern_x)
    cell.absorb(vern_y)

    label=pg.text(text=label,size=text_size,layer=layers[0])

    label.move(destination=(cell.xmax-label.xsize/2,cell.ymax-2*label.ysize))

    overlabel=pg.bbox(label.bbox,layer=layers[1])

    overlabel_scaled=dl.Device().add(gdspy.PolygonSet(overlabel.copy('tmp',scale=2).get_polygons(),layer=layers[1]))

    overlabel_scaled.move(origin=overlabel_scaled.center,\
        destination=label.center)

    cutlab=pg.boolean(label,overlabel_scaled,'xor',layer=layers[1])

    cell<<label
    cell<<cutlab

    cell=join(cell)

    return cell

def chip_frame(
    name="Default",
    size=(20e3,20e3),
    street_width=150,
    street_length=1e3,
    layer=LayoutDefault.layerTop,
    print_name=True,
    name_style=None):

    die_cell=pg.basic_die(size=size,\
        die_name="",layer=layer,draw_bbox=False,
        street_length=street_length,street_width=street_width)

    cell=dl.Device(name=name)

    cell.absorb(cell<<die_cell)

    if print_name:

        if name_style is None:

            text_cell=pc.TextParam(\
                {'size':800,\
                'label':name,\
                'location':'top',\
                'distance':Point(0,0),\
                'layer':layer}).draw()

        else:

            text_cell=name_style.draw()

        text_cell.move(origin=(text_cell.xmax,text_cell.ymax),

            destination=(cell.xmax-street_width*1.2,cell.ymax-street_width*1.2))

        cell.add(text_cell)

        cell.flatten()

    return cell

def align_TE_on_via():

    cell=dl.Device("Align TE on VIA")

    circle=pg.circle(radius=50,layer=LayoutDefault.layerVias)

    cross=pg.cross(width=30,length=250,layer=LayoutDefault.layerVias)

    g=Group([circle,cross])

    g.align(alignment='x')
    g.align(alignment='y')
    circle.add(cross)

    viapattern=pg.union(circle,'A+B',layer=LayoutDefault.layerVias)

    TEpattern=pg.union(circle,'A+B',layer=LayoutDefault.layerTop).copy('tmp',scale=0.8)

    cell.add(viapattern)
    cell.add(TEpattern)

    cell.align(alignment='x')
    cell.align(alignment='y')

    cell.flatten()

    return cell

def prompt_param_table():

    import tkinter as tk

    from tkinter import filedialog

    root = tk.Tk()

    root.withdraw()

    root.call('wm', 'attributes', '.', '-topmost', True)

    file_path = filedialog.askopenfilename()

    from IPython import get_ipython

    if get_ipython() is not None:

        get_ipython().run_line_magic('gui','qt')

    tab=pd.read_excel(file_path)

    tab.set_index(tab.columns[0],inplace=True)

    tab.index.name='Tag'

    return tab

def get_device_param_from_table(tab : pd.DataFrame, tag : str):

    pars=tab.loc[tag].to_dict()

    for name,value in pars.items():

        try:

            pars[name]=value.item()

        except:

            pass

    return pars

def alignment_marks_4layers(scale=[0.2,0.5,1]):

    def dr(cell):

        return DeviceReference(cell)

    BElayer=LayoutDefault.layerBottom
    TElayer=LayoutDefault.layerTop
    VIAlayer=LayoutDefault.layerVias
    ETCHlayer=LayoutDefault.layerEtch
    PETCHlayer=LayoutDefault.layerPartialEtch
    Zerolayer=LayoutDefault.layerPad

    align1=verniers(scale,layers=[BElayer,VIAlayer],label='VIA',reversed=True)
    align_ph=pg.bbox(align1.bbox) #only for space
    align2=verniers(scale,layers=[BElayer,TElayer],label='TE')
    align3=verniers(scale,layers=[BElayer,ETCHlayer],label='ETCH')
    align4=verniers(scale,layers=[BElayer,PETCHlayer],label='PETCH')
    t1=text_aligner(size=300,label="Align to BE",
        layers=[BElayer,TElayer,ETCHlayer,PETCHlayer,VIAlayer])
    g=Group([align1,dr(align_ph),align2,align3,align4,t1])
    g.distribute(direction='x',spacing=150)
    g.align(alignment='y')

    align5=verniers(scale,layers=[TElayer,VIAlayer],label='VIA',reversed=True)
    align6=verniers(scale,layers=[TElayer,ETCHlayer],label='ETCH')
    align7=verniers(scale,layers=[TElayer,PETCHlayer],label='PETCH')
    t2=text_aligner(size=300,label='Align to TE',\
        layers=[TElayer,ETCHlayer,PETCHlayer,VIAlayer])
    g2=Group([align5,dr(align_ph),dr(align_ph),align6,align7,t2])
    g2.distribute(direction='x',spacing=150)
    g2.align(alignment='y')

    align8=verniers(scale,layers=[Zerolayer,VIAlayer],label='VIA',reversed=True)
    align9=verniers(scale,layers=[Zerolayer,BElayer],label='BE')
    align10=verniers(scale,layers=[Zerolayer,TElayer],label='TE')
    align11=verniers(scale,layers=[Zerolayer,ETCHlayer],label='ETCH')
    align12=verniers(scale,layers=[Zerolayer,PETCHlayer],label='PETCH')
    t3=text_aligner(size=300,label='Align to Pad',\
        layers=[Zerolayer,BElayer,TElayer,ETCHlayer,PETCHlayer,VIAlayer])
    g3=Group([align8,align9,align10,align11,align12,t3])
    g3.distribute(direction='x',spacing=150)
    g3.align(alignment='y')

    g_tot=Group([g,g2,g3])
    g_tot.distribute(direction='y',spacing=150)
    g_tot.align(alignment='xmin')

    cell=Device("Alignments")

    for c in [align1,align2,align3,align4,t1]:

        cell.add(c)

    for c in [align5,align6,align7,t2]:
        cell.add(c)

    for c in [align8,align9,align10,align11,align12,t3]:
        cell.add(c)

    return cell

def add_utility_cell(cell,align_scale=[0.25,0.5,1],position=['top','left']):

    align_mark=alignment_marks_4layers(scale=align_scale)

    test_cell=resistivity_test_cell()

    align_via=Device('Align_Via')

    maskname_cell=mask_names()

    align_via.add_array(
        align_TE_on_via(),
        rows=3,
        columns=1,
        spacing=(0,350))

    align_via.flatten()

    g=Group([align_via,align_mark,test_cell])

    g.distribute(direction='x',spacing=100)

    g.align(alignment='y')

    g.move(origin=(g.center[0],g.ymax),\
        destination=(cell.center[0],\
            cell.ymax-300))

    maskname_cell.move(origin=(maskname_cell.xmin,maskname_cell.ymin),\
        destination=(test_cell.xmin,test_cell.ymax+150))

    utility_cell=Device(name="UtilityCell")

    if isinstance(position,str):

        position=[position]

    if 'top' in position:

        utility_cell<<align_mark
        utility_cell<<align_via
        utility_cell<<test_cell
        utility_cell<<maskname_cell

    if 'left' in position:

        t2=utility_cell<<align_mark
        t3=utility_cell<<align_via
        g=Group(t2,t3)

        g.rotate(angle=90,center=(t2.xmin,t2.ymin))

        g.move(origin=(t2.xmin,t2.center[1]),\
            destination=(cell.xmin,cell.center[1]))

    cell<<utility_cell

def text_aligner(
    size=300,
    label="Align to Bottom",
    layers=(
        pt.LayoutDefault.layerBottom,
        pt.LayoutDefault.layerTop,
        pt.LayoutDefault.layerVias,
        pt.LayoutDefault.layerEtch,
        pt.LayoutDefault.layerPad)
    ):

    t=pc.TextParam({'size':size,'label':label})

    cells=[]

    for l in layers:

        t.layer=l
        cells.append(t.draw())

    g=Group(cells)
    g.align(alignment='x')
    g.align(alignment='y')

    out_cell=Device()

    for c in cells:

        out_cell.add(c)

    return out_cell

def mask_names(
    names=(
        "Bottom Electrode","Top Electrode",
        "Via Layer","Etch Layer",
        "PartialEtch Layer","Pad Layer"),
    layers=(
        pt.LayoutDefault.layerBottom,
        pt.LayoutDefault.layerTop,
        pt.LayoutDefault.layerVias,
        pt.LayoutDefault.layerEtch,
        pt.LayoutDefault.layerPartialEtch,
        pt.LayoutDefault.layerPad),
    size=250):
    """ Prints array of strings on different layers.

        Mostly useful for Layer Sorting on masks.

        Parameters
        ----------
            names : iterable of str

            layers : iterable of int

            size : float

        Returns
        -------
            cell : phidl.Device.
    """

    text_param=pc.TextParam({'size':size})

    if not len(names)==len(layers):

        raise ValueError("Unbalanced mask names/layers combo")

    else:

        iter_params=[{
            name:value for name,value in zip(['label','layer'],
            [names[x],layers[x]])} for x in range(len(names))]

        text_cells=[]

        for x in iter_params:

            [text_param.set(name,value) for name,value in x.items()]

            text_cells.append(text_param.draw())

        g=Group(text_cells)

        g.distribute(direction='x',spacing=size)

        cell_name=Device(name='Mask Names')

        for x in text_cells:

            cell_name.absorb(cell_name<<x)

        return cell_name

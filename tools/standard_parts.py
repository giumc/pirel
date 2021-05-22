import phidl.geometry as pg
import phidl.device_layout as dl
import pathlib
from devices import *

def resistivity_test_cell():

    """Create cell with standard Resisistivity Test

    Returns
    ------

        cell : phidl.Device

    """

    with open(str(os.path.dirname(__file__))+'\\ResistivityTest.gds', 'rb') as infile:

        cell=pg.import_gds(infile)

        cell=join(cell)

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

            # import gdspy

            tobedel=cal.get_polygons(by_spec=(layer2,0))

            cal=cal.remove_polygons(lambda pts, layer, datatype: layer == layer2)

            replica=Device()

            replica.add(gdspy.PolygonSet(tobedel,layer=layer2))

            frame=Device()

            frame.add(pg.bbox(replica.bbox,layer=layer2))

            frame_ext=Device()

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

    overlabel_scaled=Device().add(gdspy.PolygonSet(overlabel.copy('tmp',scale=2).get_polygons(),layer=layers[1]))

    overlabel_scaled.move(origin=overlabel_scaled.center,\
        destination=label.center)

    cutlab=pg.boolean(label,overlabel_scaled,'xor',layer=layers[1])

    cell<<label
    cell<<cutlab

    cell=join(cell)

    return cell

def chip_frame(name="Default",size=(20e3,20e3),layer=LayoutDefault.layerTop,logos=None):

    street_length=size[0]/5

    street_width=150

    die_cell=pg.basic_die(size=size,\
        die_name="",layer=layer,draw_bbox=False,
        street_length=street_length,street_width=street_width)

    cell=Device(name=name)

    cell.absorb(cell<<die_cell)

    text_cell=TextParam(\
        {'size':800,\
        'label':name,\
        'location':'top',\
        'distance':Point(0,0),\
        'layer':layer}).draw()

    text_cell.move(origin=(text_cell.xmax,text_cell.ymax),\
        destination=(cell.xmax-street_width*1.2,cell.ymax-street_width*1.2))

    cell.add(text_cell)

    if logos is not None:

        if isinstance(logos,str):

            logos=pathlib.Path(logos)

        elif isinstance(logos,list) or isinstance(logos,tuple):

            cells_logo=[]

            for p in logos:

                if isinstance(p,str):

                    # import pdb ; pdb.set_trace()

                    cells_logo.append(import_gds(p))

                elif isinstance(p,pathlib.Path):

                    cells_logo.append(import_gds(str(p.absolute())))

    g=Group(cells_logo)
    g.distribute(direction='x',spacing=150)
    g.align(alignment='y')

    logo_cell=Device(name="logos")

    for c in cells_logo:

        logo_cell.add(c)

    logo_cell.flatten()

    logo3=cell<<logo_cell

    logo3.move(origin=(logo3.xmin,logo3.ymin),\
        destination=(cell.xmin+1.1*street_width,cell.ymin+1.1*street_width))

    logo4=cell<<logo_cell

    logo4.move(origin=(logo4.xmax,logo4.ymin),\
        destination=(cell.xmax-1.1*street_width,cell.ymin+1.1*street_width))

    # restest=resistivity_test_cell()
    #
    # restest.move(origin=(restest.xmin,restest.ymax),\
    #     destination=(cell.xmin+1.1*street_width,cell.ymax-1.1*street_width))

    # cell.add(restest)

    return cell

def align_TE_on_via():

    cell=Device("Align TE on VIA")

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

def dice(cell,width=100,layer=LayoutDefault.layerTop,spacing=150):

    street_length=min(cell.xsize,cell.ysize)/2.5

    die_cell=pg.basic_die(size=(cell.xsize+2*(width+spacing) , cell.ysize+2*(width+spacing)),\
            die_name="",layer=layer,draw_bbox=False,
            street_length=street_length,street_width=width)

    g=Group([die_cell,cell])

    g.align(alignment='y')

    g.align(alignment='x')

    cell.add(die_cell)

    TextParam(\
        {'size':700,\
        'label':cell.name,\
        'location':'bottom',\
        'distance':Point(0,-width-spacing/2),\
        'layer':layer}).add_text(cell)

def generate_gds_from_image(path,**kwargs):

    """ Converts a png file in gds.

        Uses nazca.image() method for the conversion.

        Parameters
        ----------
            path : str or pathlib.Path

            **kwargs : passed to nazca.image()

        Appends to input path a file with a .gds extension.

        Examples
        --------
        generate_gds_from_image( r"MyPath\\NEU logo.png",\
            layer=ld.layerTop,threshold=0.3,pixelsize=1,size=2048,invert=True)

         #will create a "MyPath\\NEU logo.gds" file.
    """

    import nazca as nd

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

    cell=Device(name=path.stem).add(pg.import_gds(str(path.absolute())))

    if flatten==True:

        cell.flatten()

    return cell

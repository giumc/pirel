import phidl.geometry as pg
import phidl.device_layout as dl
import pathlib
from sketch import *

ld=LayoutDefault

def resistivity_test_cell():

    with open(str(os.path.dirname(__file__))+'\\ResistivityTest.gds', 'rb') as infile:

        cell=pg.import_gds(infile)

        cell=join(cell)

        return cell

def verniers(scale=[1, 0.5, 0.1],layers=[1,2],label='TE',text_size=20,reversed=False):

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

            new_cal=cal<<pg.boolean(replica,frame_ext,'xor',layer=layer2)

            new_cal.move(destination=(0,dim*25))

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

    label.move(destination=(cell.xmax-label.xsize,cell.ymax-3*label.ysize))

    overlabel=pg.bbox(label.bbox,layer=layers[1])

    overlabel_scaled=Device().add(gdspy.PolygonSet(overlabel.copy('tmp',scale=2).get_polygons(),layer=layers[1]))

    overlabel_scaled.move(origin=overlabel_scaled.center,\
        destination=label.center)

    cutlab=pg.boolean(label,overlabel_scaled,'xor',layer=layers[1])

    cell<<label
    cell<<cutlab

    cell=join(cell)

    return cell
        # del xvern, xvern_y

def alignment_marks_4layers(scale=[0.2,0.5,1]):

    BElayer=ld.layerBottom
    TElayer=ld.layerTop
    VIAlayer=ld.layerVias
    ETCHlayer=ld.layerEtch
    Zerolayer=ld.layerPad

    align1=verniers(scale,layers=[BElayer,VIAlayer],label='VIA',reversed=True)
    align2=verniers(scale,layers=[BElayer,TElayer],label='TE')
    align3=verniers(scale,layers=[BElayer,ETCHlayer],label='ETCH')

    g=Group([align1,align2,align3])
    g.distribute(direction='x',spacing=150)
    g.align(alignment='y')

    align4=verniers(scale,layers=[TElayer,VIAlayer],label='VIA',reversed=True)
    align5=verniers(scale,layers=[BElayer,TElayer],label='TE')
    align6=verniers(scale,layers=[TElayer,ETCHlayer],label='ETCH')

    g2=Group([align4,align5,align6])
    g2.distribute(direction='x',spacing=150)
    g2.align(alignment='y')

    align7=verniers(scale,layers=[Zerolayer,VIAlayer],label='VIA',reversed=True)
    align8=verniers(scale,layers=[Zerolayer,TElayer],label='TE')
    align9=verniers(scale,layers=[Zerolayer,ETCHlayer],label='ETCH')

    g3=Group([align7,align8,align9])
    g3.distribute(direction='x',spacing=150)
    g3.align(alignment='y')

    g_tot=Group([g,g2,g3])
    g_tot.distribute(direction='y',spacing=150)
    g_tot.align(alignment='x')

    cell=Device("Alignments")
    cell.absorb(cell<<align1)
    cell.absorb(cell<<align2)
    cell.absorb(cell<<align3)
    cell.absorb(cell<<align4)
    # cell.absorb(cell<<align5)
    cell.absorb(cell<<align6)
    cell.absorb(cell<<align7)
    cell.absorb(cell<<align8)
    cell.absorb(cell<<align9)

    return cell

def mask_names(names=("Bottom Electrode","Top Electrode","Via Layer","Etch Layer","Pad Layer"),\
    layers=(ld.layerBottom,ld.layerTop,ld.layerVias,ld.layerEtch,ld.layerPad),\
    size=250):

    text_param=TextParam({'size':size})

    if not len(names)==len(layers):

        raise ValueError("Unbalanced mask names/layers combo")

    else:

        iter_params=[{name:value for name,value in zip(['label','layer'],[names[x],layers[x]])} for x in range(len(names))]

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

def add_utility_cells(cell,align_scale=[0.25,0.5,1],position=['top','left']):

    align_cell=alignment_marks_4layers(scale=align_scale)

    test_cell=resistivity_test_cell()

    align_via=align_TE_on_via()

    align_via_tot=draw_array(align_via,1,3,row_spacing=150,column_spacing=150)

    g=Group([align_via_tot,align_cell,test_cell])

    g.distribute(direction='x',spacing=100)

    g.align(alignment='y')

    g.move(origin=(g.xmin,g.ymax),\
        destination=(cell.center[0]-g.xsize/2,\
            cell.ymax+g.ysize/2))

    test_cell.add(align_cell)

    test_cell.add(align_via_tot)

    t2=DeviceReference(test_cell)

    maskname_cell=mask_names()

    maskname_cell.move(origin=(maskname_cell.xmin,maskname_cell.ymin),\
        destination=(test_cell.xmin,test_cell.ymax+150))

    test_cell.add(maskname_cell)

    test_cell._internal_name="UtilityCell"

    if isinstance(position,str):

        position=[position]

    if 'left' in position:

        cell<<test_cell

    if 'top' in position:

        t2=DeviceReference(test_cell)

        t2.rotate(angle=90,center=(t2.xmin,t2.ymin))

        t2.move(origin=(t2.xmin+t2.xsize/2,t2.ymin),\
            destination=(cell.xmin,cell.ymin+cell.ysize/2-t2.ysize/2))

        cell.add(t2)

def chip_frame(name="Default",size=(20e3,20e3),layer=ld.layerTop):

    street_length=size[0]/5
    street_width=300
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

    neu_cell=import_gds(r"C:\Users\giuse\Desktop\NewCode\WARP_Layout\NEU logo.gds")
    darpa_cell=import_gds(r"C:\Users\giuse\Desktop\NewCode\WARP_Layout\DARPAlogo.gds")

    g=Group([neu_cell,darpa_cell])
    g.distribute(direction='x',spacing=150)
    g.align(alignment='y')

    neu_cell.add(darpa_cell)
    logo_cell=neu_cell.flatten()
    logo_cell._internal_name="logos"
    # logo1=cell<<logo_cell
    #
    # logo1.move(origin=(logo1.xmin,logo1.ymax),\
    #     destination=(cell.xmin+2*street_width,cell.ymax-2*street_width))

    # logo2=cell<<logo_cell
    #
    # logo2.move(origin=(logo2.xmax,logo1.ymax),\
    #     destination=(cell.xmax-2*street_width,cell.ymax-2*street_width))

    logo3=cell<<logo_cell

    logo3.move(origin=(logo3.xmin,logo3.ymin),\
        destination=(cell.xmin+1.1*street_width,cell.ymin+1.1*street_width))

    logo4=cell<<logo_cell

    logo4.move(origin=(logo4.xmax,logo4.ymin),\
        destination=(cell.xmax-1.1*street_width,cell.ymin+1.1*street_width))

    restest=resistivity_test_cell()

    restest.move(origin=(restest.xmin,restest.ymax),\
        destination=(cell.xmin+1.1*street_width,cell.ymax-1.1*street_width))

    cell.add(restest)

    return cell

def align_TE_on_via():

    cell=Device("Align TE on VIA")

    circle=pg.circle(radius=50,layer=ld.layerVias)

    cross=pg.cross(width=30,length=250,layer=ld.layerVias)

    g=Group([circle,cross])

    g.align(alignment='x')
    g.align(alignment='y')
    circle.add(cross)

    viapattern=pg.union(circle,'A+B',layer=ld.layerVias)

    TEpattern=pg.union(circle,'A+B',layer=ld.layerTop).copy('tmp',scale=0.8)

    cell.add(viapattern)
    cell.add(TEpattern)

    cell.align(alignment='x')
    cell.align(alignment='y')

    cell.flatten()

    # import pdb; pdb.set_trace()

    return cell

def dice(cell,width=100,name="Default",layer=ld.layerTop):

    street_length=min(cell.xsize,cell.ysize)/2.5

    die_cell=pg.basic_die(size=(cell.xsize+500,cell.ysize+500),\
            die_name="",layer=layer,draw_bbox=False,
            street_length=street_length,street_width=width)

    die_cell._internal_name=name+"Die"

    g=Group([die_cell,cell])

    g.align(alignment='y')
    g.align(alignment='x')

    cell<<die_cell

    TextParam(\
        {'size':700,\
        'label':name,\
        'location':'bottom',\
        'distance':Point(0,0),\
        'layer':layer}).add_text(cell)

def generate_gds_from_image(path,**kwargs):

    import nazca as nd

    if isinstance(path,pathlib.Path):

        path=str(path.absolute())

    else:

        path=pathlib.Path(path)

    cell=nd.image(path,**kwargs).put()

    path=path.parent/(path.stem+".gds")

    nd.export_gds(filename=str(path.absolute()))

    return path

def import_gds(path,cellname=None,**kwargs):

    if isinstance(path,str):

        path=pathlib.Path(path)

    cell=pg.import_gds(str(path.absolute()))

    cell.flatten()

    if cellname is not None:

        cell._internal_name=cellname

    return cell

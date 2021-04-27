import phidl.geometry as pg
import phidl.device_layout as dl
from sketch import *

ld=LayoutDefault()

def resistivity_test_cell():

    with open(str(os.path.dirname(__file__))+'\\ResistivityTest.gds', 'rb') as infile:

        cell=pg.import_gds(infile)

        return join(cell)

def verniers(scale=[1, 0.5, 0.1],layers=[1,2],label='TE',text_size=20):

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

        xvern.append(pg.litho_calipers(\
            notch_size,\
            notch_spacing,\
            num_notches,\
            notch_offset,\
            row_spacing,\
            layer1,\
            layer2))

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

    align1=verniers(scale,layers=[BElayer,VIAlayer],label='VIA')
    align2=verniers(scale,layers=[BElayer,TElayer],label='TE')
    align3=verniers(scale,layers=[BElayer,ETCHlayer],label='ETCH')

    g=Group([align1,align2,align3])
    g.distribute(direction='x',spacing=150)
    g.align(alignment='y')

    cell=Device("Alignments")
    cell.absorb(cell<<align1)
    cell.absorb(cell<<align2)
    cell.absorb(cell<<align3)

    del align1, align2,align3

    return cell

def chip_frame(name="Default",size=(20e3,20e3),layer=ld.layerTop,\
    align_scale=[0.2,0.5,1]):

    die_cell=pg.basic_die(size=size,\
        die_name="",layer=layer,draw_bbox=False,
        street_length=size[0]/5,street_width=size[0]/60)

    align_cell=alignment_marks_4layers(scale=align_scale)

    test_cell=resistivity_test_cell()

    cell=Device(name="Frame")

    r1=cell<<die_cell

    LayoutPart.add_text(cell,\
        {'size':700,'label':name,\
        'location':'bottom',\
        'distance':Point(-size[0]/30,-200*2-size[0]/30),\
        'font':'BebasNeue-Regular.otf',\
    'layer':layer})

    g=Group([align_cell,test_cell])

    g.distribute(direction='x',spacing=100)

    g.align(alignment='y')

    g.move(origin=(g.xmax,g.ymax),\
        destination=(cell.xmax-g.xsize/8,\
            cell.ymax-g.ysize/2))

    test_cell.add(align_cell)

    cell<<test_cell

    test_ul=cell<<test_cell

    test_ul.move(origin=(test_ul.xmin,g.ymax),\
        destination=(cell.xmin+g.xsize/8,\
            cell.ymax-g.ysize/2))

    test_ll=cell<<test_cell

    test_ll.move(origin=(test_ll.xmin,test_ll.ymin),\
        destination=(cell.xmin+g.xsize/8,\
            cell.ymin+g.ysize))

    test_lr=cell<<test_cell

    test_lr.move(origin=(test_lr.xmax,test_lr.ymin),\
        destination=(cell.xmax-g.xsize/8,\
            cell.ymin+g.ysize/2))

    cell=join(cell)

    cell.name='Frame'

    return cell

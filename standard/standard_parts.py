import phidl.geometry as pg
import phidl.device_layout as dl
from sketch import *
def resistivity_test():

    return pg.import_gds('./ResistivityTest.gds',cellname='ResistivityTest')

def verniers(scale=[1, 0.5, 0.1],layers=[1,2],label='TE'):

    cell=dl.Device(name="verniers")

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
    g.distribute(direction='y',spacing=10)
    g.align(alignment='x')
    xcell=dl.Device(name="x")
    for x in xvern:

        xcell<<x

    xcell=join(xcell)

    xvern_x=cell<<xcell
    xvern_y=cell<<xcell

    xvern_y.rotate(angle=-90)
    xvern_y.move(destination=(xvern_x.xmax,xvern_x.ymin))

    cell.absorb(xvern_x)
    cell.absorb(xvern_y)

    return cell
        # del xvern, xvern_y

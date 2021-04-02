import LayoutClasses as lc
import os
import gdspy
import numpy as np

lib = gdspy.GdsLibrary('testfile',units=1e-6)
# idt=lc.IDT(name='x')
# cell=idt.draw()

# bus=lc.Bus()
# bus.distance=np.array([100,0])
# cell=bus.draw()

res = lc.BaseLFEResonator()
#
cell=res.draw()

lib.add(cell)

outname=lib.name+'.gds'

if os.path.exists(outname):

    os.remove(outname)

# lib.write_gds(outname)
# gdspy.GdsWriter(lib.name+'.gds')
gdspy.LayoutViewer(lib)

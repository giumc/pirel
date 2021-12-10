
import phidl.geometry as pg
import phidl.device_layout as dl

r=pg.rectangle()

p=dl.Device('parent')
rect_ref=p.add_ref(r,alias='rect_ref')

rect_ref.move(destination=(5,0))

gp=dl.Device('grandparent')
parent_ref=gp.add_ref(p,alias='parent_ref')

parent_ref.move(destination=(5,0))

print(gp['parent_ref'].parent['rect_ref'].origin)

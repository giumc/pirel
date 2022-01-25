import phidl.geometry as pg
import phidl.device_layout as dl
import pirel.pcells as pc
import pirel.modifiers as pm
import pirel.tools as pt
import pirel.addOns.standard_parts as ps

t=pc.Text('hey')
t['Label']='boom'

main_cell=t.draw()

small_t=pc.Text('h2')
small_t.size=10
small_t["Layer"]=(3,)

small_t.add_to_cell(main_cell,angle=90,anchor_source='c',anchor_dest='ur')

 # pt.check(main_cell)

# main_cell=pc.IDT("hey").draw()
main_cell.write_gds('hey')

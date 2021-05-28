import pirel.pcells as pc
import pirel.tools as pt
import pirel.modifiers as pm

from phidl.device_layout import Device,Group
import phidl
from unittest import TestCase

import unittest

class pCellTest(TestCase):

    def setUp(self):

        phidl.reset()

    def test_allclasses(self):

        for layclass in pc._allclasses:

            layobj=layclass()

            self._check_lookup(layobj)

            self._recheck_lookup(layobj)

        base_dev=pc.LFERes

        for mods in pm._allmodifiers:

            if not mods==pm.addLargeGnd:

                cell=mods(base_dev)()

                self._check_lookup(cell)
                self._recheck_lookup(cell)

    def _check_lookup(self,obj):

            obj.draw()

            map=pt.get_class_param(obj.__class__)

            pt.pop_all_match(map,".*name*")

            cmpdict=pt._get_hashable_params(obj,map)

            try:

                if cmpdict in obj._draw_lookup:

                    print(f"After first call, found cell for {obj.__class__.__name__}!")

                    self.assertTrue(cmpdict in obj._draw_lookup)

            except Exception:

                print(f"Error in {obj.__class__.__name__}!")

                print(cmpdict)

                print( obj._draw_lookup)

                self.assertTrue(cmpdict in obj._draw_lookup)

    def _recheck_lookup(self,obj):

        cell=obj.draw()

        map=pt.pop_all_match(pt.get_class_param(obj.__class__),'.*name*')

        try:

            if pt._get_hashable_params(obj,map) in obj._draw_lookup:

                print(f"Found again cell for {obj.__class__.__name__}!")

                self.assertTrue(obj._draw_lookup[pt._get_hashable_params(obj,map)]==cell)

        except Exception:

            print(f"""Device for {obj.__class__.__name__} with params
            {pt._get_hashable_params(obj,map)} should be in lookup""")

            self.assertTrue(obj._draw_lookup[pt._get_hashable_params(obj,map)]==cell)

class RoutingTest(TestCase):

    def test_routing(self):

        r=pc.Routing()

        from pirel.tools import Point

        ll=Point(500,500)
        ur=Point(1000,1000)

        r.clearance=(ll.coord,ur.coord)

        r.trace_width=50

        dx_increment=200
        dy_increment=50

        s0=Point(750,0)

        d0=Point(0,100)

        cells=[]

        gtot=[]

        master_cell=Device()

        for n in range(10):

            d0=d0+Point(dx_increment,0)

            cells.append([])

            for n in range(10):

                d0=d0+Point(0,dy_increment)

                angle=-90

                if d0.y>ll.y:

                    dt=d0+Point(0,ur.y-ll.y+10)

                    angle=90

                else:

                    dt=d0

                r.ports=(pt.Port(name='1',midpoint=s0.coord,width=r.trace_width,orientation=90),\
                        pt.Port(name='2',midpoint=dt.coord,width=r.trace_width,orientation=angle))

                try:

                    new_cell=master_cell<<r._draw_with_frame()

                except Exception as e:

                    print(e)

                    pt.check(r._draw_with_frame())

                    self.assertTrue(1==0)

                cells[-1].append(new_cell)

            g=Group(cells[-1])

            g.distribute(direction='x')

            gtot.append(g)

        g=Group(gtot)

        g.distribute(direction='y')

        pt.check(master_cell)

        self.assertTrue(1)

class MultiRoutingTest(TestCase):

    def test_routing(self):

        r=pc.MultiRouting()

        from pirel.tools import Point

        ll=Point(500,500)
        ur=Point(1000,1000)

        r.clearance=(ll.coord,ur.coord)

        r.trace_width=50

        dx_increment=200
        dy_increment=50

        s0=Point(750,0)

        d0=Point(0,100)

        cells=[]

        master_cell=Device()

        for n in range(10):

            d0=d0+Point(dx_increment,0)

            dest=[]

            for n in range(10):

                d0=d0+Point(0,dy_increment)

                angle=-90

                if d0.y>ll.y:

                    dt=d0+Point(0,ur.y-ll.y+10)

                    angle=90

                else:

                    dt=d0

                if dt.in_box(r.clearance):

                    dt=dt+Point(300,300)

                dest.append(pt.Port(name=str(n),midpoint=dt.coord,width=r.trace_width,orientation=angle))

            r.sources=(pt.Port(name='-1',midpoint=s0.coord,width=r.trace_width,orientation=90),)

            r.destinations=tuple(dest)

            try:

                new_cell=master_cell<<r.draw()
                cells.append(new_cell)

            except Exception as e:

                print(e)

                self.assertTrue(1==0)
                # import pdb; pdb.set_trace()

        g=Group(cells)

        g.distribute(direction='x')

        pt.check(master_cell)

        self.assertTrue(1)

class ParasiticAwareMultiRoutingTest(TestCase):

    def test_cell(self):

        master_cell=Device()
        obj=pc.ParasiticAwareMultiRouting()

        dx=100

        trace_width=50

        sources=(pt.Port(name='1',midpoint=(0,0),width=trace_width/2,orientation=90),)

        n_max=7

        for n in range(1,n_max):

            dest=tuple([pt.Port(
                name='d'+str(x),
                midpoint=(dx*x,trace_width*4),
                width=dx/4,
                orientation=-90)]) for x in range(-n,n)])

            obj.sources=sources
            obj.destinations=dest
            obj.trace_width=trace_width
            obj.clearance=((500,500),(1000,1000))

            master_cell<<obj.draw()

        master_cell.distribute(direction='x')
        master_cell.align(alignment='y')

        check(master_cell)


class ModifiersTest(TestCase):

    def test_modifiers_on_LFEREs(self):

        cls=pc.LFERes

        for x in pm._allmodifiers :

            if not x==pm.addLargeGnd :

                obj=x(cls)()

                print(obj.__class__.__name__)

                obj.draw()

class PEtchTest(TestCase):

    def test_draw(self):

        cell=pm.addPEtch(pc.FBERes)()

        pt.check(cell.draw())

        self.assertTrue(1)

if __name__=='__main__':
    unittest.main()


# d=addProbe(array(calibration(FBERes,'open'),4),addLargeGnd(GSGProbe))(name="DEF")
# base_params=d.export_params()
#
#
# base_params["IDTPitch"]=7
# base_params["IDTN"]=2
# base_params["IDTOffset"]=1
# base_params["IDTLength"]=100
# base_params["IDTCoverage"]=0.5
# base_params["BusSizeY"]=5
# base_params["EtchPitX"]=10
# base_params["IDTActiveAreaMargin"]=1
# base_params["AnchorSizeY"]=20
# base_params["AnchorSizeX"]=20
# base_params["AnchorXOffset"]=0
# base_params["AnchorMetalizedX"]=10
# base_params["AnchorMetalizedY"]=24
# base_params["ViaSize"]=10
# base_params["Overvia"]=2
# base_params["ViaAreaY"]=30
# base_params["ViaAreaX"]= lambda : 3*d.idt.n*d.idt.pitch
# d.import_params(base_params)
#
# print(d)
#
# import


#
# d.draw().write_gds(str(path

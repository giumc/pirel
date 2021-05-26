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

    def test_class_list(self):

        for layclass in pc._allclasses:

            layobj=layclass()

            self._check_lookup(layobj)

            layobj.draw()

    def _check_lookup(self,obj):

            obj.draw()

            map=pt.get_class_param(obj.__class__)

            pt.pop_all_match(map,".*name*")

            cmpdict=pt._get_hashable_params(obj,map)

            try:

                self.assertTrue(cmpdict in obj._draw_lookup)

            except Exception:

                print(f"Error in {obj.__class__.__name__}!")

                print(cmpdict)

                print( obj._draw_lookup)

                self.assertTrue(cmpdict in obj._draw_lookup)

    def _recheck_lookup(self,obj):

        cell=obj.draw()

        map=pt.pop_all_match(pt.get_class_param(obj.__class),'.*name*')

        try:

            self.assertTrue(obj._draw_lookup[pt._get_hashable_params(obj,map)]==cell)

        except Exception:

            print(f"""Device for {obj.__class__.__name__} with params
            {pt._get_hashable_params(obj,map)} should be in lookup""")

            self.assertTrue(obj._draw_lookup[pt._get_hashable_params(obj,map)]==cell)

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
# import pathlib
#
# d.draw().write_gds(str(path

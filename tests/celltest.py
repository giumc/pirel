import pirel.pcells as pc
import pirel.tools as pt
import pirel.modifiers as pm

from phidl.device_layout import Device,Group
import phidl
from unittest import TestCase

import unittest

tobetested=[pc.Anchor()]

class pCellTest(TestCase):

    def setUp(self):

        phidl.reset()

        self.tobetested=tobetested

    def test_class_params(self):

        for laycell in self.tobetested:

            cls_param=pt.get_class_param(laycell)
            # print(f"Params in {laycell.__class__.__name__}: ")
            # print("\n".join(cls_param))
            # print("\n")


    def test_draw(self):

        d=Device()
        ref=[]
        for laycell in self.tobetested:

            laycell.draw()

    def test_draw_lookup(self):

        cells=[]

        for laycell in self.tobetested:

            cells.append(laycell.draw())

            map=pt.get_class_param(laycell)

            cmpdict={}

            for m in map:

                cmpdict.update({m:getattr(laycell,m)})

            cmpdict.pop('name')

            if not tuple(cmpdict) in laycell._draw_lookup:

                print("bu")
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

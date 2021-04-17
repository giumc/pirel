import sketch
import numpy as np

device=sketch.DUT()

device_params=device.export_params()

device_params["ProbeSize"]=sketch.Point(150,150)
device_params["ProbeGroundPadSize"]=500

device.import_params(device_params)

array=sketch.ParametricArray()

array.device=device

array.print_params_name()

# array.param_name=["IDTPitch","EtchWidth"]
#
# array.param_value=[\
#     [5,10,20],\
#     [50,100,200]]

# array.param_name="IDTPitch"
#
# array.param_value=[_ for _ in range(50,0,-5)]

array.labels_top=None
array.labels_bottom=None

array.draw()

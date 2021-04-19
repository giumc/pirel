from pathlib import Path
import os
p=Path(os.path.dirname(__file__))
import sys
sys.path.append(str(p.parent.absolute()))

import sketch
import numpy as np

device=sketch.DUT()

device_params=device.export_params()

device_params["ProbeSize"]=sketch.Point(100,100)
device_params["ProbePitch"]=200
device_params["ProbeGroundPadSize"]=500

device.import_params(device_params)

array=sketch.ParametricArray()

array.device=device
array.x_spacing=200

param1=sketch.SweepParam({"IDTCoverage":[0.3,0.5,0.7]})
param2=sketch.SweepParam({"BusLength":[50,100,150]})

array.x_param=param1.combine(param2)

# array.x_param={"IDTCoverage": [ _ for _ in np.arange(0.2,1,0.2)],\
#     "IDTcitch":[_ for _ in np.arange(5,25,5)] }

array.auto_labels()

array.test(size=200,spacing=200)
#
# mat=sketch.ParametricMatrix("Hi")
# mat.x_spacing=200
# mat.y_spacing=400
# # mat.labels_top=None
# # mat.labels_bottom=None
#
# mat.device=device
# mat.auto_labels(top_label="HAHA",col_index=3,row_index=3)
# # print(mat.labels_top)
# # print(mat.labels_bottom)
# mat.test(size=200,spacing=50)

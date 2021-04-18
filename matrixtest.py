import sketch
import numpy as np

device=sketch.DUT()

device_params=device.export_params()

device_params["ProbeSize"]=sketch.Point(150,150)
device_params["ProbePitch"]=200
device_params["ProbeGroundPadSize"]=500

device.import_params(device_params)

array=sketch.ParametricArray()

array.device=device

array.param={"IDTCoverage": [ _ for _ in np.arange(0.2,1,0.2)],\
    "IDTPitch":[_ for _ in np.arange(5,25,5)] }

array.gen_labels()

array.test(size=200,spacing=200)

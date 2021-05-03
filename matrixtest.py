from PyResLayout import *
import numpy as np

device=addProbe(Scaled(array(LFERes,3)),addLargeGnd(GSGProbe))(name="HI")

# param=device.export_params()

# param["IDTPitch"]=7
# param["IDTN"]=4
# param["IDTYOffset"]=1
# param["IDTLength"]=10
# param["IDTCoverage"]=0.5
# param["BusSizeY"]=0.5
# param["EtchX"]=0.4
# param["AnchorSizeY"]=0.5
# param["AnchorSizeX"]=0.5
# param["AnchorEtchMarginX"]=0.2
# param["AnchorEtchMarginY"]=0.2
#
# device.import_params(param)

array=PArray(device,name="HiArray")

# array.device=paramScaled(device)
array.x_spacing=200

param1=SweepParam({"IDTCoverage":[0.3,0.5,0.7]})
param2=SweepParam({"BusSizeY":[5,10,15]})

array.x_param=param1.combine(param2)

# array.x_param={"IDTCoverage": [ _ for _ in np.arange(0.2,1,0.2)],\
#     "IDTcitch":[_ for _ in np.arange(5,25,5)] }

array.auto_labels()

array.view()

array.table.to_excel('arraytest.xlsx')

exit()
print(array.device)
#
mat=PMatrix(device,"Hi")
mat.y_param=SweepParam({"AnchorSizeX":[0.1, 0.3,0.6]})
mat.x_spacing=200
mat.y_spacing=400
# mat.labels_top=None
# mat.labels_bottom=None

# mat.device=device
mat.auto_labels(top_label="HAHA",col_index=3,row_index=3)
# print(mat.labels_top)
# print(mat.labels_bottom)
mat.view()

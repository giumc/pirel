from PyResLayout import *
import numpy as np

device=addProbe(array(Scaled(LFERes),3),addLargeGnd(GSGProbe))(name="HI")

param=device.export_params()

# print("\n".join(device.get_params_name()))

param["IDTPitch"]=7

param["IDTN"]=4

param["IDTYOffset"]=1

param["IDTLength"]=150/7

param["IDTCoverage"]=0.5

param["BusSizeY"]=0.5

param["EtchX"]=0.4

param["AnchorSizeY"]=4

param["AnchorSizeX"]=0.1

param["AnchorEtchMarginX"]=0.2

param["AnchorEtchMarginY"]=0.2

param["BusExtLength"]=5

param["ProbePitch"]=200

param["ProbeSize"]=100

param["GndRoutingWidth"]=150

device.import_params(param)

# print(device)

array=PArray(device,name="HiArray")

array.x_spacing=200

param1=SweepParam({"IDTCoverage":[0.3,0.5,0.7]})

param2=SweepParam({"BusSizeY":[2,4,8]})

array.x_param=param1.combine(param2)

# print(array)
# array.x_param={"IDTCoverage": [ _ for _ in np.arange(0.2,1,0.2)],\
#     "IDTcitch":[_ for _ in np.arange(5,25,5)] }

# array.auto_labels()

# exit()

# array.view()

# array.plot_param("AnchorSizeX")

# array.table.to_excel('arraytest.xlsx')

# array.plot_param(("IDTResistance","BusResistance",'Resistance'))

# print(array.device)

# exit()

#
mat=PMatrix(device,"Hi")
mat.x_param=param1.combine(param2)
mat.y_param=SweepParam({"AnchorSizeX":[0.1, 0.3,0.6]})

mat.x_spacing=200
mat.y_spacing=400

mat.auto_labels(col_index=3,row_index=3)

# mat.view()

fig=mat.plot_param('Resistance')

plt.figure(fig)

plt.savefig("test.svg",bbox_inches='tight')

import phidl.path as pp

from phidl import quickplot as qp

path1=pp.smooth([(0,0),(50,0)])

qp(path1)

path2=pp.smooth([(0,0),(50,0),(100,0)])

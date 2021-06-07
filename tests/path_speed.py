import phidl.path as pp
from phidl.device_layout import CrossSection
from phidl import quickplot as qp
from phidl import set_quickplot_options as qpo
import PyResLayout

from PyResLayout import Point as P

nexp=100

npoints=10

increment=3

def test_smooth():

    for _ in range(nexp):

        points=[P(0,0)]

        for n in range(1,npoints+1):

            if n%2==0:

                points.append(points[n-1]+P(0,increment))

            else:

                points.append(points[n-1]+P(increment,0))

        coords=[]

        for p in points:

            coords.append(p.coord)

        x=CrossSection()

        x.add(width=increment/10)

        cell=PyResLayout.join(x.extrude(pp.smooth(coords,radius=increment/100,num_pts=50),simplify=increment/100))

    return cell

def test_append():

    for _ in range(nexp):

        p=pp.Path()

        for n in range(1,npoints+1):

            if n%2==0:

                p.append(pp.straight(length=increment))

                p.append(pp.arc(radius=increment/100,num_pts=50,angle=-90))

            else:

                p.append(pp.straight(length=increment))

                p.append(pp.arc(radius=increment/109,num_pts=50,angle=90))

        x=CrossSection()

        x.add(width=increment/10)

        cell=PyResLayout.join(x.extrude(p,simplify=increment/100))

    return cell
# qpo(blocking=True)
# qp(test_smooth())
# qp(test_append())

import cProfile
import pstats
profile = cProfile.Profile()
profile.runcall(test_smooth)#,path=os.path.dirname(__file__),param='Resistance')
ps = pstats.Stats(profile)
ps.sort_stats('cumtime')
ps.print_stats(20)

profile = cProfile.Profile()
profile.runcall(test_append)#,path=os.path.dirname(__file__),param='Resistance')
ps = pstats.Stats(profile)
ps.sort_stats('cumtime')
ps.print_stats(20)
# qp()

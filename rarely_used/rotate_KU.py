#!/usr/bin/python
import pyfits
import numpy as np
from sys import argv
from pylab import *

list_subDARK=argv[-1]
test = np.loadtxt(list_subDARK, dtype="str")
for name in test:
    imA=pyfits.getdata(name)
    imAh=pyfits.getheader(name)
    imC = np.rot90(imA, 3)
    imC = np.fliplr(imC)
    pyfits.writeto(name[0:-5]+'_r.fits', imC, imAh)
    print name[0:-5]+"_r.fits OK"

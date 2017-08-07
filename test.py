#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. std_code.py [list name]
editor Jacob975
20170318
#################################
update log
    20170318 version alpha 1
        This code is made for convenient constructing new code.
    
    20170626 version alpha 2 
    1. change name method to Usage
    2. add VERBOSE
        In detail 
        VERBOSE == 0 means no print 
        VERBOSE == 1 means printing limited result
        VERBOSE == 2 means graphing a plot or printing more detailed result
        VERBOSE == 3 means printing debug imfo
    
    20170719 version alpha 3
    1.  delete usless part, finding stdev.
    2.  add a func of reading .tsv file.
'''
from sys import argv
import numpy as np
import matplotlib.pyplot as plt
import pyfits
import time
import curvefit
from scipy import optimize


def moments2D(inpData):
    # Returns the (amplitude, xcenter, ycenter, xsigma, ysigma, rot, bkg, e) 
    # estimated from moments in the 2d input array Data
    if len(inpData) == 0:   # check whether the matrix is a empty matrix.
        return 0
    # check whether the matrix containing np.nan
    # if True, abandan this star.
    data_list = inpData[np.isnan(inpData)]
    if len(data_list)>0:
        return 0
    bkg = 0.0
    try:
        bkg = np.median(np.hstack((inpData[:,0], inpData[:,-1], inpData[0,:], inpData[-1,:])))
    except IndexError:      # check whether the matrix is a empty matrix.
        return 0
    Data=np.ma.masked_less(inpData-bkg,0)   #Removing the background for calculating moments of pure 2D gaussian
    #We also masked any negative values before measuring moments

    amplitude = Data.max()
    total= float(Data.sum())
    Xcoords,Ycoords= np.indices(Data.shape)

    xcenter= (Xcoords*Data).sum()/total
    if np.isnan(xcenter):
        xcenter = 0.0
    ycenter= (Ycoords*Data).sum()/total
    if np.isnan(ycenter):
        ycenter = 0.0
    RowCut= Data[int(xcenter),:]  # Cut along the row of data near center of gaussian
    ColumnCut= Data[:,int(ycenter)]  # Cut along the column of data near center of gaussian
    xsigma= np.sqrt(np.ma.sum(ColumnCut* (np.arange(len(ColumnCut))-xcenter)**2)/ColumnCut.sum())
    ysigma= np.sqrt(np.ma.sum(RowCut* (np.arange(len(RowCut))-ycenter)**2)/RowCut.sum())
    #Ellipcity and position angle calculation
    Mxx= np.ma.sum((Xcoords-xcenter)*(Xcoords-xcenter) * Data) /total
    Myy= np.ma.sum((Ycoords-ycenter)*(Ycoords-ycenter) * Data) /total
    Mxy= np.ma.sum((Xcoords-xcenter)*(Ycoords-ycenter) * Data) /total
    pa= 0.5 * np.arctan(2*Mxy / (Mxx - Myy))
    rot= np.rad2deg(pa)
    return amplitude,xcenter,ycenter,xsigma,ysigma, rot,bkg

def twoD_Gaussian((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    xo = float(xo)
    yo = float(yo)    
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) 
                            + c*((y-yo)**2)))
    return g.ravel()

def FitGauss2D_curve_fit(data, ip = None):
    if ip == None:
        ip = moments2D(data)
    if ip == 0:
        return 0, 0, 0
    Xcoor, Ycoor= np.indices(data.shape)
    xdata = np.vstack((Xcoor.ravel(),Ycoor.ravel()))
    ydata = data.ravel()
    paras , cov = optimize.curve_fit(twoD_Gaussian, xdata, ydata, p0 = ip)
    return paras, cov, 1

def get_star_curve_fit(data, coor, margin = 4, half_width_lmt = 4, eccentricity = 1):
    VERBOSE= 3
    star_list = []
    # find data mean and data std
    paras_hist, cov_hist = curvefit.hist_gaussian_fitting('default', data)
    data_mean = paras_hist[0]
    data_std = paras_hist[1]
    for i in xrange(len(coor)):
        half_width = curvefit.get_half_width(data, data_mean, data_std, coor[i])
        # check the point is big enough.
        if half_width < half_width_lmt:
            continue
        # take the rectangle around some star.
        imA = data[ coor[i][0]-half_width-margin:coor[i][0]+half_width+margin, coor[i][1]-half_width-margin:coor[i][1]+half_width+margin ]
        params, cov, success = FitGauss2D_curve_fit(imA)
        if VERBOSE>2: print params
        # check the position is valid or not
        if success == 0:
            continue
        if params[1] < 0 or params[2] < 0 :
            continue
        if params[1] > 1023 or params[2] > 1023:
            continue
        if params[0] > 65535 or params[0] < 0:
            continue

        # This part is used to check whether the eccentricity is proper or not, the default is less than 0.9
        # If you cannot match img successfully, I recommand you to annotate or unannotate below script.
        if eccentricity < 1 and eccentricity >= 0:
            if params[3] > params[4]:
                long_axis = params[3]
                short_axis = params[4]
            else:
                long_axis = params[4]
                short_axis = params[3]
            # check the excentricity
            if (math.pow(long_axis, 2.0)-math.pow(short_axis, 2.0))/long_axis > eccentricity :
                continue
        if VERBOSE>2:
            # draw a figure of star
            f = plt.figure(i)
            plt.imshow(imA, vmin = imA.min() , vmax = imA.max() )
            plt.colorbar()
            plt.plot(params[1], params[2], 'ro')
            f.show()

        params[1] = coor[i][0]+params[1]-half_width-margin
        params[2] = coor[i][1]+params[2]-half_width-margin
        temp = tuple(params)
        star_list.append(temp)
    star_list = np.array(star_list, dtype = [('amplitude', float), ('xcenter', float), ('ycenter', float), ('xsigma', float), ('ysigma', float), ('rot', float), ('bkg', float)])
    return star_list

#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()
# get property from argv
fits_name=argv[-1]
# do what you want.

data = pyfits.getdata(fits_name)
peak_list = curvefit.get_peak_filter(data)
star_list = get_star_curve_fit(data, peak_list)

# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."

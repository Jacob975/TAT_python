#!/usr/bin/python
'''
Program:
    This is a liberary program of fitting , currently containning gaussian, poisson, 2D-gaussian.
Usage:
    1. from curvefit import [func name] or import curvefit
    2. use it in your lovely code.
Editor:
    Jacob975
#################################
update log
20180625 version alpha 1
    1. Remove some 
'''
import numpy as np
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import math
from astropy.io import fits as pyfits
from scipy import optimize

def gaussian(x, mu, sig, height):
    return np.power(2 * np.pi , -0.5)*np.exp(-np.power(x - mu , 2.) / (2 * np.power(sig, 2.)))/sig+height

def hist_gaussian(x, mu, sig):
    return np.power(2 * np.pi , -0.5)*np.exp(-np.power(x - mu , 2.) / (2 * np.power(sig, 2.)))/sig

def gaussian_fitting(entries):
    entries = np.array(entries)
    # flatten the array in order to fitting.
    x_plot= np.indices( entries.shape)
    entries = entries.flatten()
    x_plot = row.flatten()
    # fitting
    paras, cov = optimize.curve_fit(gaussian, x_plot, entries)
    return paras, cov

def hist_gaussian_fitting(name, data, half_width = 20, shift = 0, VERBOSE = 0):
    # 0 : no print,
    # 1 : print answer, 
    # 2 : do graph, 
    # 3 : print debug info
    # get rid of nan
    flatten_data = data[~np.isnan(data)]
    flatten_data = flatten_data[flatten_data < 100000.0]
    flatten_data = flatten_data[flatten_data > -10000.0]
    data_mean = np.mean(flatten_data)
    if math.isnan(data_mean):
        data_mean = 0.0
    # number is the number of star with this value
    # bin_edges is left edge position of each point on histagram.
    numbers, bin_edges = np.histogram(flatten_data, bins= 80, range = [data_mean - half_width + shift , data_mean + half_width + shift], normed = True)
    # find the maximum number, where will be the central of fitting figure.
    index_max = np.argmax(numbers)
    index_max = bin_edges[index_max]
    bin_middles = 0.5*(bin_edges[1:] + bin_edges[:-1])
    # initial paras
    if math.isnan(np.std(flatten_data)):
        std = 1.0
    else :
        std = np.std(flatten_data)
    moments = (data_mean, std)
    # fit 
    paras, cov = optimize.curve_fit(hist_gaussian, bin_middles, numbers, p0 = moments)
    return paras, cov

#---------------------------------------------------------------------
# current using 2D guassian fitting 

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

def Gaussian2D_leastsq(amplitude, xcenter, ycenter, xsigma, ysigma, rot,bkg):
    # Returns a 2D Gaussian function with input parameters. rotation input rot should be in degress 
    rot=np.deg2rad(rot)  #Converting to radians
    Xc=xcenter*np.cos(rot) - ycenter*np.sin(rot)  #Centers in rotated coordinates
    Yc=xcenter*np.sin(rot) + ycenter*np.cos(rot)
    #Now lets define the 2D gaussian function
    def Gauss2D(x,y) :
        # Returns the values of the defined 2d gaussian at x,y 
        xr=x * np.cos(rot) - y * np.sin(rot)  #X position in rotated coordinates
        yr=x * np.sin(rot) + y * np.cos(rot)
        return amplitude*np.exp(-(((xr-Xc)/xsigma)**2 +((yr-Yc)/ysigma)**2)/2) +bkg

    return Gauss2D

def FitGauss2D_leastsq(Data,ip=None):
    """ 
    Fits 2D gaussian to Data with optional Initial conditions ip=(amplitude, xcenter, ycenter, xsigma, ysigma, rot, bkg)
    Example:
    >>> X,Y=np.indices((40,40),dtype=np.float)
    >>> Data=np.exp(-(((X-25)/5)**2 +((Y-15)/10)**2)/2) + 1
    >>> FitGauss2D(Data)
    (array([  1.00000000e+00,   2.50000000e+01,   1.50000000e+01, 5.00000000e+00,   1.00000000e+01,   2.09859373e-07, 1]), 2)
    
                 amplitude          xcenter         ycenter          xsigma            ysigma              rot      bkg   success=1,2,3,4
    """
    if ip is None:   #Estimate the initial parameters form moments and also set rot angle to be 0
        ip=moments2D(Data) 
    if ip == 0:
        return 0, 100
    Xcoords,Ycoords= np.indices(Data.shape)
    def errfun(ip):
        dXcoords= Xcoords-ip[1]
        dYcoords= Ycoords-ip[2]
        Weights=np.sqrt(np.square(dXcoords)+np.square(dYcoords)) # Taking radius as the weights for least square fitting
        return np.ravel((Gaussian2D_leastsq(*ip)(*np.indices(Data.shape)) - Data)/np.sqrt(Weights))  
        #Taking a sqrt(weight) here so that while scipy takes square of this array it will become 1/r weight.

    p, success = scipy.optimize.leastsq(errfun, ip)

    return p,success

#----------------------------------------------------------------
# This is 2D gaussian fitting program with curve_fit method
# moments is shared with leastsq method

def FitGaussian_curve_fit((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    xo = float(xo)
    yo = float(yo)
    a = (np.cos(theta)**2)/(2.0*sigma_x**2) + (np.sin(theta)**2)/(2.0*sigma_y**2)
    b = -(np.sin(2.0*theta))/(4.0*sigma_x**2) + (np.sin(2.0*theta))/(4.0*sigma_y**2)
    c = (np.sin(theta)**2)/(2.0*sigma_x**2) + (np.cos(theta)**2)/(2.0*sigma_y**2)
    g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2.0*b*(x-xo)*(y-yo)
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
    paras = []
    cov = []
    try:
        paras , cov = optimize.curve_fit(FitGaussian_curve_fit, xdata, ydata, p0 = ip)
    except:
        return 0, 0, 0
    else:
        return paras, cov, 1

#---------------------------------------------------------------------
# star matching program
# include how to find the peak of a image
# and how to find the center and brightness of a gaussian star.

# This is a code for finding stdev and mean of a image.
# The way in concept: find stdev and mean for all image.
# Then wipe out whose larger than 3 times of stdev.
# Find stdev and mean again, the 2nd result will be return.
''' Currently it is useless, because histogram method is much more accurate.'''
def get_mean_std(data, times = 3):
    temp_data = data[:,:]
    # sometimes we will deal with np.nan, we need the skip nan and go on.
    temp_data = temp_data[~np.isnan(temp_data)]
    collector = temp_data[np.where(temp_data < np.mean(temp_data) + times*np.std(temp_data))]
    fits_mean = np.mean(collector)
    fits_stdev = np.std(collector)
    return fits_mean, fits_stdev

def get_peak_filter(data, tall_limit = 10, size = 5, VERBOSE = 0):
    # get mean and noise by histgram.
    paras, cov = hist_gaussian_fitting('default', data)
    data_mean = paras[0]
    data_std = paras[1]
    # create a maximum filter and minimum filter.
    data_max = filters.maximum_filter(data, size)
    maxima = (data == data_max)
    data_min = filters.minimum_filter(data, size)
    # tall_limit * data_std + data_mean is threshold about how sensitive about this code
    diff = ((data_max - data_min) > tall_limit * data_std + data_mean)
    # maxima is a np.array, edge of shape will be set 1, others set 0.
    maxima[diff == 0] = 0
    # labeled is a np.array, denote the edge of each shape with different index numbers.
    # num_object is a number of how many different object you found.
    # example in this website: https://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.ndimage.measurements.label.html
    labeled, num_objects = ndimage.label(maxima)
    slices = ndimage.find_objects(labeled)
    # list up all center of shape you found.
    x, y = [], []
    for dy,dx in slices:
        x_center = (dx.start + dx.stop - 1)/2
        x.append(x_center)
        y_center = (dy.start + dy.stop - 1)/2
        y.append(y_center)
    if VERBOSE>0:
        print "number of peaks is :", len(x)
    coor = zip(y, x)
    return coor

def get_peak_title():
    answer = np.array(["xcenter", "ycenter"])
    return answer

def get_peak(data, tall_limit = 10, VERBOSE = 0):
    # get property about data distriution
    paras, cov = hist_gaussian_fitting('default', data)
    data_mean = paras[0]
    data_std = paras[1]
    if VERBOSE>0 : print "mean:", data_mean, "std:", data_std
    is_tall = np.where(data >= data_mean + tall_limit  * data_std)
    is_tall = zip(is_tall[0], is_tall[1])
    peak_list = []
    for pos in is_tall:
        # check whether the point is larger than others
        boolm_tall = True
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                x = pos[0] + i
                y = pos[1] + j
                try :
                    if data[x,y] == np.nan:
                        boolm_tall = False
                    elif data[x,y] > data[pos]:
                        boolm_tall = False
                except :
                    continue
        if boolm_tall == True:
            peak_list.append(pos)
    #print "number of peaks is :", len(peak_list)
    return peak_list

def get_half_width(data, data_mean, data_std, pos):
    # This is a func to return to half_width of a star territory.
    half_width = 1
    while True:
        try:
            if data[pos[0], pos[1]+half_width] <= data_mean + 3 * data_std:
                break
        except:
            return 0
        else:
            if half_width > 20:
                return 0
            half_width = half_width + 2
    return half_width

def get_star_title(detailed = False):
    answer = np.array([])
    if detailed:
        answer = np.array(['amplitude', 'e_amplitude', 'xcenter', 'e_xcenter', 'ycenter', 'e_ycenter', 'xsigma', 'e_xsigma', 'ysigma', 'e_ysigma', 'rot', 'e_rot', 'bkg', 'e_bkg'])
    else :
        answer = np.array(['amplitude', 'xcenter', 'ycenter', 'xsigma', 'ysigma', 'rot', 'bkg'])
    return answer

def get_star_unit(detailed = False):
    if detailed:
        answer = np.array(['count', 'count', 'pixel', 'pixel', 'pixel','pixel','pixel','pixel','pixel','pixel','degree','degree','count','count'])
    else:
        answer = np.array(['count', 'pixel', 'pixel', 'pixel', 'pixel','degree','count'])
    return answer

def get_star(data, coor, margin = 4, half_width_lmt = 4, eccentricity = 1, detailed = False, VERBOSE = 0):
    star_list = []
    # find data mean and data std
    paras_hist, cov_hist = hist_gaussian_fitting('default', data)
    data_mean = paras_hist[0]
    data_std = paras_hist[1]
    for i in xrange(len(coor)):
        half_width = get_half_width(data, data_mean, data_std, coor[i])
        # check the point is big enough.
        if half_width < half_width_lmt:
            continue
        # take the rectangle around some star.
        imA = data[ coor[i][0]-half_width-margin:coor[i][0]+half_width+margin, coor[i][1]-half_width-margin:coor[i][1]+half_width+margin ]
        params, cov, success = FitGauss2D_curve_fit(imA)
        if VERBOSE>1:
            print "star_{2}: {0}, {1}".format(coor[i][0], coor[i][1], i)
            print params, cov, success
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
        # Turn local coord into image coor.
        params[1] = coor[i][0]+params[1]-half_width-margin
        params[2] = coor[i][1]+params[2]-half_width-margin
        if detailed:
            error = np.sqrt(cov)
            temp = (params[0], error[0,0], params[1], error[1,1], params[2], error[2,2], params[3], error[3,3], params[4], error[4,4], params[5], error[5,5], params[6], error[6,6])
        else:
            temp = tuple(params)
        star_list.append(temp)
    if detailed:
        star_list = np.array(star_list, dtype = [('amplitude', float), ('e_amplitude', float), ('xcenter', float), ('e_xcenter', float), ('ycenter', float), ('e_ycenter', float), ('xsigma', float), ('e_xsigma', float), ('ysigma', float), ('e_ysigma', float), ('rot', float), ('e_rot', float), ('bkg', float), ('e_bkg', float)])
    else:
        star_list = np.array(star_list, dtype = [('amplitude', float), ('xcenter', float), ('ycenter', float), ('xsigma', float), ('ysigma', float), ('rot', float), ('bkg', float)])
    return star_list

#---------------------------------------------------------------------
# Take noise and effective exptime from a list of image
# noise is calculated by hist_gaussian_fitting above.

def get_noise_median_method(fits_list, VERBOSE = 0):
    data_list = np.array([])
    # get exposure time
    imhA = pyfits.getheader(fits_list[0])
    exptime = imhA['EXPTIME']
    for i in xrange(len(fits_list)):
        data = pyfits.getdata(fits_list[i])
        if i == 0:
            data_list = np.array([data])
        else :
            data_list = np.append(data_list, [data], axis = 0)
    sum_fits = np.median(data_list, axis = 0)
    paras, cov = hist_gaussian_fitting("Untitle", sum_fits, shift = -7)
    data_std = paras[1]/exptime
    return exptime*len(fits_list), data_std

def get_noise_mean_method(fits_list, VERBOSE = 0):
    sum_fits = []
    # get exposure time
    imhA = pyfits.getheader(fits_list[0])
    exptime = imhA['EXPTIME']
    for i in xrange(len(fits_list)):
        data = pyfits.getdata(fits_list[i])
        if i == 0:
            sum_fits = data
        else:
            sum_fits = np.add(sum_fits, data)
    div_fits = np.divide(sum_fits, len(fits_list))
    paras, cov = hist_gaussian_fitting("Untitle", div_fits, shift = -7)
    data_std = paras[1]/exptime
    return exptime*len(fits_list), data_std


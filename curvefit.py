#!/usr/bin/python
'''
Program:
This is a liberary program of fitting , currently containning gaussian, poisson, 2D-gaussian.
method:
1. from curvefit import [func name] or import curvefit
2. use it in your lovely code.
editor Jacob975
#################################
update log
    20170320 version alpha 1 
    add func stdev, gaussian, gaussian_fitting, poisson, poisson_fitting
    where poisson_fitting is sensitive in original.
    In other word, poisson_fitting fucn cannot fit data which has large lambda.

    20170321 version alpha 2
    delete func stdev, because of the bad efficiency.
    improve the efficiency of all func.

    20170326 version alpha 3
    add a function to find the center of a 2-D gaussion curve.

    20170328 version alpha 4
    add a function to fitting 2D gaussian distribution.

    20170402 version alpha 5
    delete the func to find the center of a 2-S gaussion curve.
    add a new error func fitting func.
    rename all gaussion series funcs as gaussion,
    only distribute them by input

    20170402 version alpha 6
    add a func to fit lots of star with a star data list, named gau2Dlist.

    20170422 version alpha 7
    add a new extensive func to find out the position of stars after gaussian 2D fitting.

    20170508 version alpha 8 
    add three new func in match fits district.
    one is get local maximum of a image, named get_peak
    another is get the position of stars of a image, named get_star.
    final is calculate inner product, named get_inner_prod

    20170518 version alpha 9 
    A new bug outbreak in hist_gaussian_fitting.
    It cannot fit any gaussian now.

    20170519 version alpha 10 
    fix the bug of hist_gaussian_fitting
    no new added func.

    20170706 version alpha 11
    add a new func, get_noise_median_method and get_noise_mean_method
    both of them are used to find the noise of a list of matched images.

    20170717 version alpha 12
    1.  add a new func, error_transmission and its belongs
        It can calculate error transmission of a array of data
    2.  add a transformation between mag and count.
        all details is writen in comment.

    20170721 version alpha 13
    1.  add comment of get_peak

    2017728 version alpha 14
    1.  improve the efficiency of get_star
    2.  Update 2D gaussian fitting, now it could return error of each quantities.
'''
import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import math
import pyfits
from numpy import pi, r_
from scipy.misc import factorial
from scipy import optimize
from scipy.signal import argrelextrema

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

def hist_gaussian_fitting(name, data, half_width = 20, shift = 0):
    # 0 : no print,
    # 1 : print answer, 
    # 2 : do graph, 
    # 3 : print debug info
    VERBOSE = 0
    # get rid of nan
    flatten_data = data[~np.isnan(data)]
    flatten_data = flatten_data[flatten_data < 100000.0]
    flatten_data = flatten_data[flatten_data > -10000.0]
    if VERBOSE>2:print len(flatten_data)
    data_mean = np.mean(flatten_data)
    if math.isnan(data_mean):
        data_mean = 0.0
    if VERBOSE>2:print data_mean
    # number is the number of star with this value
    # bin_edges is left edge position of each point on histagram.
    # patches control each rectangle's property..
    fig = plt.figure(name)
    numbers, bin_edges, patches = plt.hist(flatten_data, bins= 80, range = [data_mean - half_width + shift , data_mean + half_width + shift], normed = True)
    # find the maximum number, where will be the central of fitting figure.
    index_max = np.argmax(numbers)
    index_max = bin_edges[index_max]
    if VERBOSE>2:print "numbers: ", numbers
    bin_middles = 0.5*(bin_edges[1:] + bin_edges[:-1])
    if VERBOSE>2:print "bin_middles: ",bin_middles
    # initial paras
    if math.isnan(np.std(flatten_data)):
        std = 1.0
    else :
        std = np.std(flatten_data)
    moments = (data_mean, std)
    if VERBOSE>2:print moments
    # fit 
    paras, cov = optimize.curve_fit(hist_gaussian, bin_middles, numbers, p0 = moments)
    if VERBOSE>3:
        # draw
        x_plot = np.linspace(index_max+ half_width+ shift, index_max- half_width+ shift, 500)
        plt.plot(x_plot, hist_gaussian(x_plot, paras[0], paras[1]), 'r-', lw= 2)
        axes = plt.gca()
        axes.set_xlim([index_max-half_width+shift, index_max+half_width+shift])
        fig.show()
    if VERBOSE>0:
        print "paras: ", paras
        print "cov: \n", cov
    return paras, cov

def poisson(k, lamb, shift):
    return (lamb**(k-shift)/factorial(k-shift)) * np.exp(-lamb)

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
    paras = []
    cov = []
    try:
        paras , cov = optimize.curve_fit(FitGaussian_curve_fit, xdata, ydata, p0 = ip)
    except:
        return 0, 0, 0
    else:
        return paras, cov, 1

#----------------------------------------------------
# fitting function in mag unit
def pow_function_mag(x, amp, const):
    return amp * np.log10(x) + const

# initial value of fitting for pow_function in mag unit
def moment_pow_fitting_mag(x_plt, value):
    const = value[0]
    amp = (value[0] - value[-1])/(np.log10(x_plt[0]) - np.log10(x_plt[-1]))
    return (amp, const)

# fitting
def pow_fitting_mag(x_plt, value):
    moment = moment_pow_fitting_mag(x_plt, value)
    paras, cov = optimize.curve_fit(pow_function_mag, x_plt, value, p0 = moment)
    return paras, cov

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

def get_star(data, coor, margin = 4, half_width_lmt = 4, eccentricity = 1, detailed = False):
    VERBOSE= 0
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
        # Turn local coord into image coor.
        params[1] = coor[i][0]+params[1]-half_width-margin
        params[2] = coor[i][1]+params[2]-half_width-margin
        if detailed:
            temp = (params[0], cov[0,0], params[1], cov[1,1], params[2], cov[2,2], params[3], cov[3,3], params[4], cov[4,4], params[5], cov[5,5], params[6], cov[6,6])
        else:
            temp = tuple(params)
        star_list.append(temp)
    if detailed:
        star_list = np.array(star_list, dtype = [('amplitude', float), ('e_amplitude', float), ('xcenter', float), ('e_xcenter', float), ('ycenter', float), ('e_ycenter', float), ('xsigma', float), ('e_xsigma', float), ('ysigma', float), ('e_ysigma', float), ('rot', float), ('e_rot', float), ('bkg', float), ('e_bkg', float)])
    else:
        star_list = np.array(star_list, dtype = [('amplitude', float), ('xcenter', float), ('ycenter', float), ('xsigma', float), ('ysigma', float), ('rot', float), ('bkg', float)])
    return star_list

# calculate the inner product and error of two side, from star_1 to star_2 and from star_1 to star_3.
def inner_product(star_1, star_2, star_3):
    try:
        x_part_1 = math.pow(star_1[1] - star_2[1], 2)
        x_error_1 = (math.pow(star_1[3], 2) + math.pow(star_2[3], 2))/x_part_1
        x_part_2 = math.pow(star_1[1] - star_3[1], 2)
        x_error_2 = (math.pow(star_1[3], 2) + math.pow(star_3[3], 2))/x_part_2
        y_part_1 = math.pow(star_1[2] - star_2[2], 2)
        y_error_1 = (math.pow(star_1[4], 2) + math.pow(star_2[4], 2))/y_part_1
        y_part_2 = math.pow(star_1[2] - star_3[2], 2)
        y_error_2 = (math.pow(star_1[4], 2) + math.pow(star_3[4], 2))/y_part_2
        inner_prod = (star_1[1] - star_2[1])*(star_1[1] - star_3[1]) + (star_1[2] - star_2[2])*(star_1[2] - star_3[2])
        var = x_part_1*x_part_2*(x_error_1 + x_error_2) + y_part_1*y_part_2*(y_error_1 + y_error_2)
        error = math.pow(var, 0.5)
    except : 
        return 0, 0
    else:
        return inner_prod, error

# check the number of matching inner prod of two stars, then return the number.
def relation_counter(ref_star, star, error):
    valid_inner_prod = 0
    for ref_inner_prod in ref_star:
        for i in xrange(len(star)):
            if ref_inner_prod <= star[i] + error[i] and ref_inner_prod >= star[i] - error[i]:
                valid_inner_prod = valid_inner_prod + 1
                continue
    return valid_inner_prod

# choose a star as a target, than choose two else the calculate the inner product.
def get_inner_product(star_list):
    inner_prod_star_list = []
    inner_prod_error_list = []
    # choose a star, named A
    for i in xrange(len(star_list)):
        inner_prod_star = np.array([])
        inner_prod_error = np.array([])
        # choose two else stars, named B and C, to get inner product of two side AB and AC.
        for j in xrange(len(star_list)):
            if i == j:
                continue
            for k in xrange(len(star_list)):
                if k == i:
                    continue
                if k <= j:
                    continue
                inner_prod, error = inner_product(star_list[i], star_list[j], star_list[k])
                inner_prod_star = np.append(inner_prod_star, inner_prod)
                inner_prod_error = np.append(inner_prod_error, error)
        # set all inner product as a list, seems like DNA of this star
        inner_prod_star_list.append(inner_prod_star)
        inner_prod_error_list.append(inner_prod_error)
    inner_prod_star_list = np.array(inner_prod_star_list)
    inner_prod_error_list = np.array(inner_prod_error_list)
    return inner_prod_star_list, inner_prod_error_list

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

#--------------------------------------------------------------------
# This is a func to wipe out exotic number in a list
# This one is made for matching images
def get_rid_of_exotic_severe(value_list, VERBOSE = 0):
    if VERBOSE>0:print value_list
    std = np.std(value_list)
    # resursive condition
    if std < 1 :
        return value_list
    mean = np.mean(value_list)
    # get the error of each value to the mean, than delete one with largest error.
    temp_value_list = value_list[:]
    sub_value_list = np.subtract(temp_value_list, mean)
    abs_value_list = np.absolute(sub_value_list)
    index_max = np.argmax(abs_value_list)
    temp_value_list= np.delete(temp_value_list, index_max)
    # check if the list is not exotic, if not, get in to recursive.
    value_list = get_rid_of_exotic_severe(temp_value_list)
    return value_list

# This one is made for scif calculation
def get_rid_of_exotic(value_list):
    std = np.std(value_list)
    mean = np.mean(value_list)
    # get the error of each value to the mean, than delete one with largest error.
    temp_value_list = np.subtract(value_list, mean)
    abs_value_list = np.absolute(temp_value_list)
    for i in xrange(len(abs_value_list)):
        if abs_value_list[i] >= 3 * std:
            value_list = np.delete(value_list, i)
    if len(abs_value_list) != len(value_list):
        value_list = get_rid_of_exotic(value_list)
    return value_list

def get_rid_of_exotic_vector(value_list, additional):
    std = np.std(value_list)
    mean = np.mean(value_list)
    # get the error of each value to the mean, than delete one with largest error.
    temp_value_list = np.subtract(value_list, mean)
    abs_value_list = np.absolute(temp_value_list)
    for i in xrange(len(abs_value_list)):
        if abs_value_list[i] >= 3 * std:
            value_list = np.delete(value_list, i)
            additional = np.delete(additional, i)
    if len(abs_value_list) != len(value_list):
        value_list, additional = get_rid_of_exotic_vector(value_list, additional)
    return value_list, additional

#---------------------------------------------------------------------
# This is a code to do error transmission calculation.
# If you got answer 0, 0 , which means you fail.
def error_transmission(value_array, error_array, sign = ""):
    # test does user specify the sign of arthemetic.
    try :
        No_sign = sign == ""
    except:
        print "Please Specify the sign of Arithmetic"
        print "Usage: error_transmission(value_array, error_array, sign == \"+\")"
        return 0, 0
    else:
        if No_sign:
            print "Please Specify the sign of Arithmetic"
            print "Usage: error_transmission(value_array, error_array, sign == \"+\")"
            return 0, 0
    value_array = np.array(value_array, dtype = float)
    error_array = np.array(error_array, dtype = float)
    answer = 0
    error = 0
    # do calculate
    if sign == "+" :
        answer = np.sum(value_array)
        error = plus_sub_error_transmission(error_array)
    elif sign == "-" :
        # hint: only two elements is acceptable, no more neither less
        answer = value_array[0] - value_array[1]
        error = plus_sub_error_transmission(error_array)
    elif sign == "*" :
        answer, error = multi_error_transmission(value_array, error_array)
    elif sign == "/" :
        # hint: only two elements is acceptable, no more neither less
        answer, error = div_error_transmission(value_array, error_array)
    else:
        print "Please Specify the sign of Arithmetic"
        print "Usage: error_transmission(value_array, error_array, sign == \"+\")"
    return answer, error

def plus_sub_error_transmission(error_array):
    # prototype: error = sqrt(a_error^2 + b_error^2 + ...)
    error_array = np.square(error_array)
    error_square = np.sum(error_array)
    error = np.sqrt(error_square)
    return error

def multi_error_transmission(value_array, error_array):
    # prototype: error = amp * sqrt((a_sigma/a)^2 + (b_sigma/b)^2 + ...)
    # where amp = a*b
    amp_list  = np.cumprod(value_array)
    amp = amp_list[-1]
    answer_array = np.divide(error_array, value_array)
    answer_array = np.square(answer_array)
    answer = np.sum(answer_array)
    answer = amp * np.sqrt(answer)
    return amp, answer
def div_error_transmission(value_array, error_array):
    # prototype: error = amp * sqrt((a_sigma/a)^2 + (b_sigma/b)^2)
    # where amp = a/b
    # hint: only two elements is acceptable, no more neither less
    if len(value_array) != 2:
        return 0, 0
    amp = np.divide(value_array[0], value_array[1])
    answer_array = np.divide(error_array, value_array)
    answer_array = np.square(answer_array)
    answer = np.sum(answer_array)
    answer = amp * np.sqrt(answer)
    return amp, answer
#---------------------------------------------------------------------
# This is a code to transfer between mag and count

def mag2count(mag, error_mag = 0):
    # prototype: count = 10^(mag / -2.5), return count
    temp_1 = np.divide(mag, -2.5)
    count = np.power(10, temp_1)
    if error_mag != 0:
        temp_2 = np.add(mag, error_mag)
        temp_2 = np.divide(temp_2, -2.5)
        error_count = np.power(10, temp_2) - np.power(10, temp_1)
    # if needn't to deal with error, just return the value
    elif error_mag == 0:
        error_count = 0
        return count
    return count, error_count

def count2mag(count, error_count = 0):
    # prototype: mag = -2.5 * log10( count ), return mag
    mag = -2.5*np.log10(count)
    if error_count != 0:
        temp = np.add(count, error_count)
        error_mag = -2.5*np.log10(count) + 2.5*np.log10(temp)
    # if needn't to deal with error, just return the value
    elif error_count == 0:
        error_mag = 0
        return mag
    return mag, error_mag

#---------------------------------------------------------------------
# basic fits processing

# This is used to read a list of fits name
def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

# This is used to rotate img
# The direction needed to modified.
def rotate(telescope, fits_list):
    if telescope == "KU":
        for name in fits_list:
            imA=pyfits.getdata(name)
            imAh=pyfits.getheader(name)
            imC = np.rot90(imA, 3)
            imC = np.fliplr(imC)
            pyfits.writeto(name[0:-5]+'_r.fits', imC, imAh)
            print name[0:-5]+"_r.fits OK"
    elif telescope == "TF":
        for name in fits_list:
            imA=pyfits.getdata(name)
            imAh=pyfits.getheader(name)
            imC = np.rot90(imA, 2)
            imC = np.fliplr(imC)
            pyfits.writeto(name[0:-5]+'_r.fits', imC, imAh)
            print name[0:-5]+"_r.fits OK"
    return

# This is used to generate subDARK fits
# lsit_name should be a list of fits name
def subtract_list(list_name, dark_name):
    fits_list = readfile(list_name)
    dark = pyfits.getdata(dark_name)
    for name in fits_list:
        imA = pyfits.getdata(name)
        imAh = pyfits.getheader(name)
        imB = np.subtract(imA, dark)
        pyfits.writeto(name[:-5]+"_subDARK.fits", imB, imAh)
        print name[:-5]+"_subDARK.fits, OK"
    return

# This is used to generate divFLAT fits
# list_name should be a list of fits name
def division_list(list_name, flat_name):
    fits_list = readfile(list_name)
    flat = pyfits.getdata(flat_name)
    for name in fits_list:
        imA = pyfits.getdata(name)
        imAh = pyfits.getheader(name)
        imB = np.divide(imA, flat)
        pyfits.writeto(name[0:-5]+"_divFLAT.fits",imB,imAh)
    print name[0:-5]+"_divFLAT.fits, OK "
    return

#---------------------------------------------------------------------


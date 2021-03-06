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
20181105 version alpha 2
    1. Revise and fix some problem on gaussian fitting 
    2. remove alternative way to fit 2D gaussian because I rarely use it
'''
import numpy as np
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
from astropy.io import fits as pyfits
from scipy import optimize
from uncertainties import ufloat, unumpy
import matplotlib.pyplot as plt

def gaussian(x, amp, mu, sig, const):
    return amp * np.exp(-np.power(x - mu , 2.) / (2 * np.power(sig, 2.))) + const

def nonC_gaussian(x, amp, mu, sig):
    return amp * np.exp(-np.power(x - mu , 2.) / (2 * np.power(sig, 2.)))

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
    if np.isnan(data_mean):
        data_mean = 0.0
    # number is the number of star with this value
    # bin_edges is left edge position of each point on histagram.
    numbers, bin_edges = np.histogram(flatten_data, bins= 80, range = [data_mean - half_width + shift , data_mean + half_width + shift], normed = True)
    # find the maximum number, where will be the central of fitting figure.
    index_max = np.argmax(numbers)
    index_max = bin_edges[index_max]
    bin_middles = 0.5*(bin_edges[1:] + bin_edges[:-1])
    moments = (0.1, data_mean, 5.)
    # fit 
    paras, cov = optimize.curve_fit(nonC_gaussian, bin_middles, numbers, p0 = moments)
    if VERBOSE > 0:
        plt.bar(bin_middles, numbers)
        plt.plot(bin_middles, nonC_gaussian(bin_middles, *paras), c= 'r')
        plt.show()
    return paras, cov

#---------------------------------------------------------------------
# current using 2D guassian fitting 

def moments2D(inpData, PSF = False):
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
    if PSF:
        return [amplitude,xcenter,ycenter,rot,bkg]
    else:
        return [amplitude,xcenter,ycenter,xsigma,ysigma,rot,bkg]

def gaussian_2d((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    xo = float(xo)
    yo = float(yo)
    a =     (np.cos(theta)**2)/(2.0*sigma_x**2) \
        +   (np.sin(theta)**2)/(2.0*sigma_y**2)
    b = -   (np.sin(2.0*theta))/(4.0*sigma_x**2) \
        +   (np.sin(2.0*theta))/(4.0*sigma_y**2)
    c =     (np.sin(theta)**2)/(2.0*sigma_x**2) \
        +   (np.cos(theta)**2)/(2.0*sigma_y**2)
    g =     offset \
        +   amplitude*np.exp(   - (a*((x-xo)**2) \
                                + 2.0*b*(x-xo)*(y-yo) \
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
        paras , cov = optimize.curve_fit(gaussian_2d, xdata, ydata, p0 = ip)
    except:
        return 0, 0, 0
    else:
        return paras, cov, 1

def PSF_phot(data, u_sigma_x = None, u_sigma_y = None, ip = None):
    # Find the initial moments
    if ip == None:
        ip = moments2D(data, PSF = True)
    if ip == 0:
        return 0, 0, 0
    # Start to do curvefit
    Xcoor, Ycoor= np.indices(data.shape)
    xdata = np.vstack((Xcoor.ravel(),Ycoor.ravel()))
    ydata = data.ravel()
    paras = []
    cov = []
    def PSF_2d((x, y), amplitude, xo, yo, theta, offset):
        return gaussian_2d((x,y), amplitude, xo, yo, u_sigma_x.n, u_sigma_y.n, theta, offset)
    try:
        paras , cov = optimize.curve_fit( PSF_2d, xdata, ydata, p0 = ip)
    except:
        return 0, 0, 0
    else:
        return paras, cov, 1

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

def get_star(data, coor, margin = 4, half_width_lmt = 4, VERBOSE = 0):
    star_list = []
    # find data mean and data std
    paras_hist, cov_hist = hist_gaussian_fitting('default', data)
    hist_mean = paras_hist[1]
    hist_std = paras_hist[2]
    for i in xrange(len(coor)):
        half_width = get_half_width(data, hist_mean, hist_std, coor[i])
        # Check if the point is big enough.
        if half_width < half_width_lmt:
            continue
        # Take the rectangle around some star.
        imA = data[ coor[i][0]-half_width-margin : coor[i][0]+half_width+margin, 
                    coor[i][1]-half_width-margin : coor[i][1]+half_width+margin ]
        params, cov, success = FitGauss2D_curve_fit(imA)
        if VERBOSE>1:
            print "star_{2}: {0}, {1}".format(coor[i][0], coor[i][1], i)
            print params
            print cov
            print success
        # Check if the position is valid or not
        if success == 0:
            continue
        if params[1] < 0 or params[2] < 0 :
            continue
        if params[1] > data.shape[0] or params[2] > data.shape[1]:
            continue
        # Check if the count is valid.
        if params[0] > 65535 or params[0] < 0:
            continue
        # Turn local coord into image coor.
        params[1] = coor[i][0]+params[1]-half_width-margin
        params[2] = coor[i][1]+params[2]-half_width-margin
        npix = len(imA) * len(imA[0])
        error = np.sqrt(cov)
        temp = [params[0], error[0,0],  # amp
                params[1], error[1,1],  # x_center
                params[2], error[2,2],  # y_center
                params[3], error[3,3],  # x_sigma
                params[4], error[4,4],  # y_sigma
                params[5], error[5,5],  # PA
                params[6], error[6,6],  # sky
                npix]
        star_list.append(temp)
    return np.array(star_list)

# calculate the flux via the parameters
# The star list should comming from get_star()
def get_flux(image, coor, u_sigma_x, u_sigma_y, VERBOSE = 0):
    star_list = []
    margin = 8
    for i in xrange(len(coor)):
        # Take the rectangle around some star.
        imA = image[coor[i][0]-margin : coor[i][0]+margin, 
                    coor[i][1]-margin : coor[i][1]+margin ]
        params, cov, success = PSF_phot(imA, u_sigma_x, u_sigma_y)
        if VERBOSE == 1:
            print "star_{2}: {0}, {1}".format(coor[i][0], coor[i][1], i)
            print params, u_sigma_x, u_sigma_y
            print cov
            print success
        if VERBOSE == 2:
            fig = plt.figure()
            plt.imshow(imA)
            plt.scatter(margin, margin)
            plt.show()
        # Check if the position is valid or not
        if success == 0:
            continue
        if params[1] < 0 or params[2] < 0 :
            continue
        if params[1] > image.shape[0] or params[2] > image.shape[1]:
            continue
        # Check if the count is valid.
        if params[0] > 65535 or params[0] < 0:
            continue
        # Turn local coord into image coor.
        params[1] = coor[i][0]+params[1]-margin
        params[2] = coor[i][1]+params[2]-margin
        npix = len(imA) * len(imA[0])
        error = np.sqrt(cov)
        temp = [params[0], error[0,0], 
                params[1], error[1,1], 
                params[2], error[2,2], 
                u_sigma_x.n, u_sigma_x.s,
                u_sigma_y.n, u_sigma_y.s,
                params[3], error[3,3], 
                params[4], error[4,4], 
                npix]
        star_list.append(temp)
    #----------------------------------------
    # After star list
    star_array = np.asarray(star_list)
    # Load amp, sig_x, and sig_y
    u_amp = unumpy.uarray(star_array[:,0], star_array[:,1])
    u_sig_x = unumpy.uarray(star_array[:,6], star_array[:,7])
    u_sig_y = unumpy.uarray(star_array[:,8], star_array[:,9])
    # calculate the flux via the result of gaussian integration.
    u_flux = (u_amp / 2) * np.pi**2 /(u_sig_x * u_sig_y)
    flux = unumpy.nominal_values(u_flux)
    e_flux = unumpy.std_devs(u_flux)
    ans_star_array = np.zeros((len(star_array), len(star_array[0]) + 2))
    ans_star_array[:,:2] = np.transpose(np.array([flux, e_flux]))
    ans_star_array[:,2:] = star_array
    return ans_star_array

#---------------------------------------------------------------------
# star matching program
# include finding the peaks in images
# and finding the center and brightness as gaussian star.

def get_peak_filter(data, tall_limit = 10, size = 5, VERBOSE = 0):
    # get mean and noise by histgram.
    paras, cov = hist_gaussian_fitting('default', data)
    data_amp = paras[0]
    data_mean = paras[1]
    data_std = paras[2]
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
    data_amp = paras[0]
    data_mean = paras[1]
    data_std = paras[2]
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
    data_std = paras[2]/exptime
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
    data_std = paras[2]/exptime
    return exptime*len(fits_list), data_std


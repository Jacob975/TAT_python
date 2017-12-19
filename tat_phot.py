#!/usr/bin/python
'''
Program:
This is a program to code to apertrue photometry and psf photometry.
Currently, because psf phot haven't been done, option of psf photometry isn't available.

we have three kinds of phot now
1. aperture phot
2. gaussian wavelet phot
3. self point spread func phot

Usage:
1. tat_phot.py [image]

example:
    tat_phot.py image.fits      # star catalog and region of this image will be generated.

editor Jacob975
20170927
#################################
update log

20170927 version alpha 1
    apertrue part work well.

20170928 version alpha 2
    add specification of psf photometry

20170929 version alpha 3
    add specification of wcs controller

20171004 version alpha 4
    1. wcs controller is done, haven't been tested.

20171012 version alpha 5
    1. wcs controller is tested.

20171014 version alpha 6
    1. outline of psf phot done. 

20171015 version alpha 7
    1. add psf theo model.

20171019 version alpha 8 
    1. Deconvolve and convolve in scipy.signal only support 1D array, not 2D and more.

20171023 version alpha 9
    1. wiener deconvolve have been done
    2. The model is bad so I got a blur processed image.

20171103 version alpha 10
    1. test mode of deconvolution is on
    2. RL algorithm is done.
    3. Now we face a problem of ripple on restored image.

20171205 version alpha 11
    1. new aper phot is already done, the previous one will be rename as gaussian_wavelet_phot.
    2. new proper parameters for DAOStarFinder
    3. psf fitting pause.

20171214 version alpha 12
    1. rename type of phot
    2. old aperphot -> gaussianphot
    3. test aperphot -> aperphot, real aperphot, also put wcs convertor into aperphot.
'''
from sys import argv
from photutils.detection import IRAFStarFinder, DAOStarFinder
from astropy.stats import gaussian_sigma_to_fwhm
from curvefit import hist_gaussian_fitting, get_peak_filter, get_star, get_star_unit, get_star_title, get_rid_of_exotic_vector, unit_converter, FitGaussian_curve_fit, FitGauss2D_curve_fit
from astropy.table import Table, Column
from tat_datactrl import readfile
from skimage import restoration 
import numpy as np
import TAT_env
import pyfits
import pywcs
import time
import warnings
from scipy.signal import convolve2d
import scipy
import aper_test

# This is used to control argus.
class argv_controller:
    fits_list = []
    def __init__(self, argu):
        self.fits_list = self.get_fitsname(argu[-1])
        return
    def get_fitsname(self, name):
        name_list = name.split(".")
        if name_list[-1] == "fits" or name_list[-1] == "fit":
            fits_list = [name]
        else:
            fits_list=tat_datactrl.readfile(name)
        return fits_list

# This class is for finding basic paras of image.
class parameter:
    data = None
    bkg = 0.0
    std = 0.0
    sigma = 0.0
    date = ""
    scope = ""
    band = ""
    method = ""
    obj = ""
    filtr = ""
    exptime = 0.0
    property_name_array = np.array(["date", "scope", "band", "method", "object"])
    def __init__(self, data):
        self.data = data
        self.sigma = self.get_sigma()
        paras, cov = hist_gaussian_fitting('default', data)
        self.bkg = paras[0]
        self.std = paras[1]
        return
    # This def is used to find the average sigma of a star
    def get_sigma(self):
        data = self.data
        # peak list is a list contain elements with position tuple.
        sz = 30
        tl = 5
        peak_list = get_peak_filter(data, tall_limit = tl,  size = sz)
        # star list is a list contain elements with star in this fits
        hwl = 4
        ecc = 1
        star_list = get_star(data, peak_list, half_width_lmt = hwl, eccentricity = ecc)
        proper_star_list = self.proper_sigma(star_list, 3, 4)
        x_sigma = np.array([column[3] for column in proper_star_list])
        y_sigma = np.array([column[4] for column in proper_star_list])
        sigma = np.average([x_sigma, y_sigma], axis = None)
        return sigma
    # find coordinate and flux of a star by aperture photometry.
    def proper_sigma(self, star_list, pos_xsigma, pos_ysigma):
        # take out all inproper value
        # for example inf and nan
        nosigular_star_list = []
        for column in star_list:
            if np.inf in column:
                continue
            elif np.nan in column:
                continue
            nosigular_star_list.append(column)
        # in x direction
        x_sigma = [column[pos_xsigma] for column in nosigular_star_list]
        proper_x_sigma, proper_star_list = get_rid_of_exotic_vector(x_sigma, nosigular_star_list, 3)
        # in y direction
        y_sigma = [column[pos_ysigma] for column in proper_star_list]
        proper_y_sigma, proper_star_list = get_rid_of_exotic_vector(y_sigma, proper_star_list, 3)
        return proper_star_list
    # get property of images from path
    def observator_property(self, image_name):
    	# get exptime from header
        imAh = pyfits.getheader(image_name)
        exptime = float(imAh["EXPTIME"])
        self.exptime = float(imAh["EXPTIME"])
        # get info from name
        image_name_list = image_name.split("_")
    	try:
            self.scope = image_name_list[0]
            self.date = image_name_list[1]
            self.obj = image_name_list[2]
            self.band = image_name_list[3]
            self.filtr = "{0}_{1}".format(image_name_list[3], image_name_list[4])
        # if name is not formated, get info from path	
        except:
            print "Inproper name, get property changing ot dir"
            path = os.getcwd()
            list_path = path.split("/")
            self.scope = list_path[-5]
            self.date = list_path[-3]
            self.obj = list_path[-2]
            self.filtr = list_path[-1]
            temp_list = self.filtr.split("_")
            self.band = temp_list[0]
    	self.method = image_name_list[-2]
    	return

# This class is for find the coordinate of stars and save region file by aperture photometry.
class gaussianphot(parameter):
    data = None
    dao_table = None
    star_table = None
    VERBOSE = 2
    def __init__(self, paras, data, VERBOSE = 2):
        self.data = data
        self.VERBOSE = VERBOSE
        # find peak by dao finder
        daofind = DAOStarFinder(threshold = 3.0*paras.std + paras.bkg , fwhm=paras.sigma*gaussian_sigma_to_fwhm, roundhi=1.0, roundlo=-1.0, sharplo=0.5, sharphi=2.0, sky = paras.bkg)
        dao_table = daofind.find_stars(paras.data)
        if self.VERBOSE>2:
            print dao_table
        self.dao_table = dao_table
        # do aperture photometry
        self.star_table = self.fit()
        return
    def fit(self):
        dao_table = self.dao_table
        data = self.data
        x_list = [int(i) for i in dao_table["ycentroid"]]
        y_list = [int(i) for i in dao_table["xcentroid"]]
        peak_list = zip(x_list, y_list)
        hwl = 3
        ecc = 1
        star_list = get_star(data, peak_list, half_width_lmt = hwl, eccentricity = ecc, detailed = True, VERBOSE = 1)
        # exclude some star will weird sigma 
        proper_star_list = self.proper_sigma(star_list, 6, 8)
        if self.VERBOSE>1:
            print "number of star = {0}".format(len(star_list))
            print "number of proper star = {0}".format(len(proper_star_list))
        # set the unit and title of params in table
        star_title = get_star_title(detailed = True)
        star_unit = get_star_unit(detailed = True)
        star_table = Table(rows = proper_star_list, names = star_title)
        for i in xrange(len(star_unit)):
            star_table[star_title[i]].unit = star_unit[i]
        self.star_table = star_table
        return star_table

# This class is for find the coordinate of stars and save region file by aperture photometry.
class aperphot(parameter):
    data = None
    dao_table = None
    star_table = None
    VERBOSE = 2
    def __init__(self, paras, data, VERBOSE =2):
        self.data = data
        self.VERBOSE = 2
        # find peak by dao finder
        daofind = DAOStarFinder(threshold = 3.0*paras.std + paras.bkg, fwhm=paras.sigma*gaussian_sigma_to_fwhm, roundhi=1.0, roundlo=-1.0, sharplo=0.5, sharphi=2.0, sky = paras.bkg)
        dao_table = daofind.find_stars(paras.data)
        if self.VERBOSE>2: print dao_table
        self.dao_table = dao_table
        # do aperture photometry
        self.star_table = self.phot()
        return

    def phot(self, rd = 12, ibd = 16, obd = 18, shape = "circle"):
        dao_table = self.dao_table
        data = self.data
        x_list = [int(i) for i in dao_table["ycentroid"]]
        #print x_list
        y_list = [int(i) for i in dao_table["xcentroid"]]
        #print y_list
        peak_list = zip(x_list, y_list)
        star_list = []
        #print peak_list
        for p in peak_list:
            x = p[0]
            y = p[1]
            # ---------------------------------
            # make sure the data is usable.
            try:
                star_data = data[x-obd:x+obd , y-obd:y+obd]
            except:
                continue
            if x-obd<0 or x+obd >= len(data):
                #print "x-obd = {0}".format(x-obd)
                #print "x+obd = {0}".format(x+obd)
                continue
            if y-obd<0 or y+obd >= len(data):
                continue
            #----------------------------------
            # rd means the radius of region of star
            # ibd means the minimun of radius of bkg
            # obd means the maximun of radius of bkg
            # shape mean the shape used to fitting
            student = aper_test.aper_phot(star_data, rd, ibd, obd, shape, name = peak_list.index(p), VERBOSE = 0)
            if student.flux < 0:
                continue
            if student.flux == np.nan:
                continue
            if student.bkg == np.nan:
                continue
            if student.e_bkg = np.nan:
                continue
            star_row = np.array([x, y, student.flux, student.bkg, student.e_flux ])
            star_list.append(star_row)
        if self.VERBOSE>2: raw_input("pause, please press enter to go on.")
        # set the unit and title of params in table
        star_title = np.array(['xcenter', 'ycenter', 'flux', 'bkg', 'e_bkg'])
        star_unit = np.array(['pixel', 'pixel', 'count', 'count', 'count'])
        star_table = Table(rows = star_list, names = star_title)
        for i in xrange(len(star_unit)):
            star_table[star_title[i]].unit = star_unit[i]
        self.star_table = star_table
        return star_table

# This is a class for save star table and star region file by psf photometry.
class psfphot(gaussianphot):
    data = None
    psfed_data = None
    psfed_r_data = None
    psfed_i_data = None
    psf_model = None
    psf_theo_model = None
    dao_table = None
    star_table = None
    VERBOSE = 0
    def __init__(self, paras, data, it = 30):
        self.data = data
        self.paras = paras
        # find peak by dao finder
        daofind = DAOStarFinder(threshold = 3.0*paras.std + paras.bkg, fwhm=paras.sigma*gaussian_sigma_to_fwhm, roundhi=1.0, roundlo=-1.0, sharplo=0.5, sharphi=2.0, sky = paras.bkg)
        dao_table = daofind.find_stars(paras.data)
        self.dao_table = dao_table
        # find stars by dao table
        self.star_table = self.fit()
        # select top 10 bright stars from star table
        self.selected_star_table = self.table_selector(self.star_table, "amplitude")
        # setup psf model
        self.psf_model = self.make_model(data, self.selected_star_table)
        self.psf_theo_model = self.make_theo_model(self.psf_model)
        # for test richardson_lucy deconvolution
        '''
        psf = np.ones((5, 5)) / 25
        camera = convolve2d(self.data, psf, 'same')
        pyfits.writeto("blurred_image.fits", camera, clobber = True)
        '''
        self.psfed_data = self.RL_deconvolution(self.psf_theo_model, self.data, it)
        self.psfed_data = np.real(self.psfed_data)
        '''
        pyfits.writeto("restored_image.fits", self.psfed_data, clobber = True)
        '''
        # for skimage wiener deconvolution
        '''
        self.psfed_data = self.skimage_wiener_deconvolution(self.psf_model, self.data, self.psf_theo_model)
        '''
        # for wiener deconvolution
        '''
        self.psfed_data = self.wiener_deconvolution(self.psf_theo_model, self.data)
        '''
        # for save real part and image part for test.
        '''
        self.psfed_r_data = np.real(self.psfed_data)
        pyfits.writeto("realpart.fits", self.psfed_r_data, clobber = True)
        self.psfed_i_data = np.imag(self.psfed_data)
        pyfits.writeto("imagpart.fits", self.psfed_i_data, clobber = True)
        '''
        self.psfed_data = np.real(self.psfed_data)
        # set the bkg the same as origin data.
        params, cov = hist_gaussian_fitting('default', self.psfed_data)
        psfed_bkg = params[0]
        self.psfed_data = np.multiply(self.psfed_data, np.divide(self.paras.bkg, psfed_bkg))
        return
    def table_selector(self, star_table, keyword):
        # sort by amplitude
        bright_sorted_star_table = star_table.sort(keyword)
        # select bright star from a star table
        selected_star_table = star_table[-50:-31]
        print selected_star_table
        return selected_star_table
    def make_model(self, data, selected_star_table):
        if VERBOSE>0: print "------   building psf model   ------"
        psf_model = None
        star_region_list = np.array([None for i in range(len(selected_star_table))])
        weight_list = np.array([None for i in range(len(selected_star_table))])
        # collect normalized bright star
        for i in xrange(len(selected_star_table)):
            # collect an area
            xc = int(selected_star_table[i]['xcenter'])
            yc = int(selected_star_table[i]['ycenter'])
            if VERBOSE>2:print "coor = {0}, {1}".format(xc, yc)
            hw = int(5*self.paras.std)
            star_region = data[xc-hw:xc+hw, yc-hw:yc+hw]
            # wipe out nan
            nan_list = star_region[np.isnan(star_region)]
            if len(nan_list)>0:
                continue
            star_region = star_region - selected_star_table[i]['bkg']
            # get basic property
            psum = np.sum(star_region)
            weight = np.sqrt(psum)
            # find the weight, If weight is nan, skip.
            if weight == None:
                continue
            else :
                weight_list[i] = np.sqrt(psum)
            # redirect the position of star
            # normalized
            normalized_star_region = np.divide(star_region, psum)
            '''
            pyfits.writeto("star_{0}.fits".format(i+1), normalized_star_region, clobber = True)
            '''
            star_region_list[i] = normalized_star_region
        print weight_list
        # stack all of models
        psf_model = np.average(star_region_list, weights = weight_list, axis = 0)
        # normalized
        psf_model = np.divide(psf_model, np.sum(psf_model))
        '''
        psf_model = np.roll(psf_model, len(psf_model)/2, axis = 0)
        psf_model = np.roll(psf_model, len(psf_model)/2, axis = 1)
        '''
        pyfits.writeto("psf_model.fits", psf_model, clobber = True)
        return psf_model
    def make_theo_model(self, psf_model):
        # do 2D guassian fitting on psf_model
        params, cov, success = FitGauss2D_curve_fit(psf_model)
        # reform theory model
        # regenerate model by parameters.
        psf_theo_model = np.fromfunction(lambda i, j:FitGaussian_curve_fit((i, j), params[0], params[1], params[2], params[3], params[4], params[5], params[6])
                , psf_model.shape, dtype = float)
        psf_theo_model = psf_theo_model.reshape(psf_model.shape)
        # normalized to summantion  = 1
        psf_theo_model = np.divide(psf_theo_model, np.sum(psf_theo_model))
        # save psf theo model
        pyfits.writeto("psf_theo_model.fits", psf_theo_model, clobber = True)
        return psf_theo_model
    def wiener_deconvolution(self, impulse_response, output_signal):
        if VERBOSE>0: print "------ wiener deconvolution ------"
        output_signal[np.isnan(output_signal)] = self.paras.bkg
        # Wiener deconvolution is an application of the Wiener filter to the noise problems inherent in deconvolution.
        # find SNR ratio
        snr = scipy.stats.signaltonoise(output_signal, axis = None)
        F_snr = scipy.stats.signaltonoise(output_signal, axis = None)
        # find impulse response in freq domain
        F_impulse_response = np.fft.fft2(impulse_response, s = [len(output_signal), len(output_signal)])
        square_F_impulse_response = np.multiply(F_impulse_response, np.conj(F_impulse_response))
        F_output_signal = np.fft.fft2(output_signal)
        # find G
        # assume G, where X^{hat} = G * Y
        G_impulse_response = np.multiply(np.divide(1, F_impulse_response), 
                np.divide(square_F_impulse_response, square_F_impulse_response + np.divide(1, F_snr)))
        F_input_signal = np.multiply(G_impulse_response, F_output_signal)
        #F_input_signal = np.divide(G_impulse_response, F_output_signal)
        input_signal = np.fft.ifft2(F_input_signal)
        # move back to right position
        input_signal = np.roll(input_signal, len(impulse_response)/2, axis = 0)
        input_signal = np.roll(input_signal, len(impulse_response)/2, axis = 1)
        return input_signal

    def RL_deconvolution(self, impulse_response, output_signal, it = 30):
        # Richardson_Lucy is a wide-used algorithm to solve blur image.
        # the goal is find latent image from a noisy and blurred image
        output_signal[np.isnan(output_signal)] = self.paras.bkg
        input_signal = output_signal
        for i in range(it):
            input_conv_impulse = convolve2d(input_signal, impulse_response, 'same')
            normalized_output_signal = np.divide(output_signal, input_conv_impulse)
            trans_impulse_response = impulse_response[::-1,::-1]
            coef = convolve2d(normalized_output_signal, trans_impulse_response, 'same')
            input_signal = np.multiply(coef, input_signal)
            name = "RLA_{0}.fits".format(i)
            pyfits.writeto(name, input_signal, clobber = True)
        return input_signal

# This class is for control processing photometry
# There are three options, psfphot, gaussianphot and aperphot.

# 1. aperphot means aperture photometry 
# program will fitting 2D gaussian distribution on each peak to test whether it is a star?

# 2. psfphot mean psf photometry,
# This part haven't been done.
class phot_control:
    data = None
    psfed_data = None
    dao_table = None
    star_table = None
    mag_table = None
    paras = None
    VERBOSE = 2
    fits_name = "untitle.fits"
    star_table_name = "untitle_table.fits"
    result_region_name = "untitle_region"
    dao_table_name = "untitle_dao_table.fits"
    dao_region_name = "untitle_dao_region"
    # opt_list is used to save the possible choice of photometry 
    opt_list = ["aperphot", "gaussianphot", "psfphot"]
    # opt is the photometry you choosed.
    opt = "aperphot"
    def __init__(self, fits_name, opt, VERBOSE = 2):
        if VERBOSE>0: print "---      start process      ---" 
        # name setting
        self.fits_name = fits_name
        self.data = pyfits.getdata(fits_name)
        self.star_table_name = "{0}_table.fits".format(self.fits_name[0:-5])
        self.result_region_name = "{0}_region".format(self.fits_name[0:-5])
        self.dao_table_name = "{0}_dao_table.fits".format(self.fits_name[0:-5])
        self.dao_region_name = "{0}_dao_region".format(self.fits_name[0:-5])
        self.VERBOSE = VERBOSE
        # test aperphot is better or psfphot?
        self.paras = parameter(self.data)
        self.paras.observator_property(fits_name)
        # three option:
        # 1. aperphot
        # 2. gaussianphot
        # 3. psfphot
        if opt == "aperphot":
            self.star_table, self.dao_table = self.aperphot(self.paras, self.data)
            self.mag_table = self.star_table
        if opt == "gaussianphot":
            self.star_table, self.dao_table = self.guassianphot(self.paras, self.data)
            self.mag_table = self.star_table
        if opt == "psfphot":
            self.header = pyfits.getheader(fits_name)
            # do wiener deconvolution recursively
            for i in xrange(1):
                if i == 0:
                    self.psfed_data = self.psfphot(self.paras, self.data, it = 30)
                else:
                    pass
                    # for RL deconvolve
                    self.psfed_data = self.psfphot(self.paras, self.data, it = i+1)
                    # for wiener deconvolve
                    self.psfed_data = self.psfphot(self.paras, self.psfed_data)
                
                result_name = "{0}_psf{1}.fits".format(self.fits_name[0:-5], i+1)
                pyfits.writeto(result_name, self.psfed_data, self.header, clobber = True)
        
        if opt != "psfphot":
            # I comment this part below because I am using aper test, there is no e_amp to used.
            # get info of del mag
            path_of_result = TAT_env.path_of_result
            path_of_del_mag = "{0}/{1}".format(path_of_result, "limitation_magnitude_and_noise/delta_mag.fits")
            del_mag_table = Table.read(path_of_del_mag)
            # add more property info table
            self.match_del_mag_table = self.observertory_property(del_mag_table, self.paras)
            wcs_ctrl = wcs_controller(self.star_table, self.match_del_mag_table, fits_name)
            self.mag_table = wcs_ctrl.mag_table
        return
    # get del mag
    def observertory_property(self, del_mag_table, paras):
        if self.VERBOSE>0: print "------   find match del mag   ------"
        # create a empty list with length of property list
        property_name_array = paras.property_name_array
        property_list = [paras.date, paras.scope, paras.band, paras.method, paras.obj]
        temp_list = [ None for i in range(len(property_name_array)) ]
        # append original list to back
        # It wiil seem as
        # temp_list = [   [], [], [], ... ,[tar_list]  ]
        temp_list.append(del_mag_table)
        for i in xrange(len(property_name_array)):
            if self.VERBOSE>0:print "current property = ",property_list[i]
            for tar in temp_list[i-1]:
                if tar[property_name_array[i]] == property_list[i]:
                    if temp_list[i] == None:
                        temp_list[i] = Table(tar)
                    else:
                        temp_list[i].add_row(tar)
        if len(temp_list[len(property_list)-1]) == 0:
            if self.VERBOSE>0:print "No matched data."
            return None
        match_del_mag_table = temp_list[len(property_list)-1]
        if self.VERBOSE>2: print match_del_mag_table 
        return match_del_mag_table
    # this def is for cut origin image into several piece. 
    # In order to get much more accurate psf model and fitting result.
    def puzzing(self, data):
        return puzz_data
    # do psf fitting, powered by psfphot.
    def psfphot(self, paras, data, it):
        if self.VERBOSE>0: print "---      psfphot star      ---"
        psffitting = psfphot(paras, data, it)
        star_table = None
        dao_table = None
        psfed_data = psffitting.psfed_data
        return psfed_data
    def aperphot(self, paras, data):
        if self.VERBOSE>0: print "---      aperphot star      ---"
        aperfitting = aperphot(paras, data)
        star_table = aperfitting.star_table
        dao_table = aperfitting.dao_table
        return star_table, dao_table
    def gaussianphot(self, paras, data):
        if self.VERBOSE>0: print "---      gaussianphot star      ---"
        gaussianfitting = gaussianphot(paras, data)
        star_table = gaussianfitting.star_table
        dao_table = gaussianfitting.dao_table
        return star_table, dao_table
    # save result of photometry.
    def save(self):
        if self.VERBOSE>0: print "---      save table      ---"
        star_table = self.star_table
        dao_table = self.dao_table
        # save table
        self.mag_table.write(self.star_table_name, overwrite = True)
        # save header to that table
        hdulist = fits.open(self.star_table_name, mode = 'update')
        prihdr = hdulist[0].header
        prihdr['DATE'] = self.paras.date
        prihdr['BAND'] = self.paras.band
        prihdr['SCOPE'] = self.paras.scope
        prihdr['METHOD'] = self.paras.method
        prihdr['EXPTIME'] = self.paras.exptime
        hdulist.flush()
        hdulist.close()
        # save star region
        region_file = open(self.result_region_name, "a")
        x_list = star_table["ycenter"]
        y_list = star_table["xcenter"]
        for i in xrange(len(x_list)):
            region_file.write("{0} {1}\n".format(x_list[i], y_list[i]))
        region_file.close()
        # save dao table
        dao_table.write(self.dao_table_name, overwrite = True)
        # save header to that table
        hdulist = fits.open(self,dao_table_name, mode = 'update')
        prihdr = hdulist[0].header
        prihdr['DATE'] = self.paras.date
        prihdr['BAND'] = self.paras.band
        prihdr['SCOPE'] = self.paras.scope
        prihdr['METHOD'] = self.paras.method
        prihdr['EXPTIME'] = self.paras.exptime
        hdulist.flush()
        hdulist.close()
        # save dao region
        region_file = open(self.dao_region_name, "a")
        x_list = dao_table["xcentroid"]
        y_list = dao_table["ycentroid"]
        for i in xrange(len(x_list)):
            region_file.write("{0} {1}\n".format(x_list[i], y_list[i]))
        region_file.close()
        return

# This is a code to control pywcs
class wcs_controller(unit_converter):
    star_table = None
    wcs_table = None
    inst_table = None
    mag_table = None
    VERBOSE = 2
    # usually, mag_table is result_table
    result_table = None
    match_del_mag_table = None
    fits_name = ""
    def __init__(self, star_table, match_del_mag_table, fits_name, VERBOSE = 2):
        if VERBOSE>0: print "---      start to process wcs      ---"
        self.fits_name = fits_name
        self.star_table = star_table
        self.match_del_mag_table = match_del_mag_table
        self.VERBOSE = VERBOSE
        # get wcs coords
        self.wcs_table = self.pix2wcs(star_table, fits_name)
        if self.VERBOSE>2: print self.wcs_table
        # get instrument mag
        self.inst_table = self.pix2mag(self.wcs_table, fits_name)
        if self.VERBOSE>2: print self.inst_table
        # get real mag
        self.mag_table = self.realmag(self.inst_table, match_del_mag_table)
        if self.VERBOSE>2: print self.mag_table
        return
    # convert star table into wcs table
    def pix2wcs(self, star_table, fits_name):
        if self.VERBOSE>0: print "------   convert pixel to wcs   ------"
        # initialized wcs
        try:
            hdulist = pyfits.open(fits_name)
            wcs = pywcs.WCS(hdulist[0].header)
        except:
            print "{0} have no wcs file".format(name)
            return None
        # convert pixel to wcs
        # initialized info
        column_name = ["RAJ2000", "DECJ2000"]
        collection =  {'RA':None, 'DEC':None}
        column_unit = ['hhmmss', 'ddmmss']
        wcs_table = star_table
        # grap data from table
        xcenter = np.array(star_table["ycenter"], dtype = float)
        ycenter = np.array(star_table["xcenter"], dtype = float)
        # arrange data
        coors = np.dstack((xcenter, ycenter))
        # convert pixel into wcs
        sky = wcs.wcs_pix2sky(coors[0], 1)
        collection['RA'] = np.array([column[1] for column in sky])                                      # result 1
        collection['DEC'] = np.array([column[0] for column in sky])                                     # result 2
        # consider error part
        try:
            # grab data from table, and test whether they exist or not.
            e_xcenter = np.array(star_table["e_ycenter"], dtype = float)
            e_ycenter = np.array(star_table["e_xcenter"], dtype = float)
        except:
            pass
        else:
            # if error of position is saved, find out the error of wcs.
            # initialized info of error
            column_err_name = ["e_RAJ2000", "e_DECJ2000"]
            collection_err = { 'e_RA':None, 'e_DEC':None}
            column_err_unit = ['hhmmss', 'ddmmss']
            eRA_coors = np.dstack((xcenter + e_xcenter, ycenter))
            eDEC_coors = np.dstack((xcenter, ycenter + e_ycenter))
            eRA_sky = wcs.wcs_pix2sky(eRA_coors[0], 1)
            eDEC_sky = wcs.wcs_pix2sky(eDEC_coors[0], 1)
            collection_err['e_RA'] = np.array([column[1] for column in eRA_sky]) - collection['RA']             # result 3
            collection_err['e_DEC'] = np.array([column[0] for column in eDEC_sky]) - collection['DEC']          # result 4
            # save the error of wcs
            i = 0
            for key, value in collection_err.iteritems():
                new_col = Column(value, name=column_err_name[i], unit = column_err_unit[i])
                wcs_table.add_column(new_col, index = i)
                i += 1
        # save the value of wcs
        # the reason of write the scipt here is that I want to keep the value in front of error.
        i = 0
        for key, value in collection.iteritems():
            new_col = Column(value, name=column_name[i], unit = column_unit[i])
            wcs_table.add_column(new_col, index = i)
            i += 1
        return wcs_table
    def pix2mag(self, star_table, fits_name):
        if self.VERBOSE>0: print "------   convert count to mag   ------"
        # initailized info
        column_name = ["mag", "e_mag"]
        collection = { 'mag':None, 'e_mag':None} 
        column_unit = ['mag_per_sec', 'mag_per_sec']
        # grab data from argument
        mag_table = star_table
        imh = pyfits.getheader(fits_name)
        exptime = imh["EXPTIME"]
        # convert count into mag
        try:
            count_per_t = np.array(star_table["amplitude"], dtype = float)/exptime
            e_count_per_t = np.array(star_table["e_amplitude"], dtype = float)/exptime
        except:
            return star_table
        mag, e_mag = self.count2mag(count_per_t, e_count_per_t)	
        collection['mag'] = mag
        collection['e_mag'] = e_mag
        # save result into table
        if all([x == np.nan for x in mag]) or all([x == np.nan for x in e_mag]):
            return None
        i = 0
        for key, value in collection.iteritems():
            new_col = Column(value, name=column_name[i], unit=column_unit[i])
            mag_table.add_column(new_col, index = len(mag_table[0]))
            i += 1
        return mag_table
    # get real magnitude
    def realmag(self, star_table, match_del_mag_table):
        if self.VERBOSE>0: print "------   convert inst mag to real mag   ------"
        # initailized info 
        local_name = ['U', 'B', 'V', 'R', 'I', 'N']
        mag_unit = 'mag_per_sec'
        # grab data from argument
        try:
            mag_array = np.array(star_table['mag'], dtype = float)
            e_mag_array = np.array(star_table['e_mag'], dtype = float)
        except:
            return star_table
        band_list = match_del_mag_table['band']
        del_mag_array = np.array(match_del_mag_table['delta_mag'], dtype = float)
        e_del_mag_array = np.array(match_del_mag_table['e_delta_mag'], dtype = float)
        mag_table = star_table
        for i in xrange(len(band_list)):
            print "This is {0} round, band is {1}".format(i+1, band_list[i])
            new_mag_name = "{0}_mag".format(band_list[i])
            e_new_mag_name = "e_{0}_mag".format(band_list[i])
            new_mag_array = mag_array - del_mag_array[i]
            e_new_mag_array = np.sqrt(np.power((e_mag_array), 2) + np.power(e_del_mag_array, 2)) # <--- It is wrong now.
            new_col = Column(new_mag_array, name = new_mag_name, unit = mag_unit)
            mag_table.add_column(new_col, index = len(mag_table[0]))
            e_new_col = Column(e_new_mag_array, name = e_new_mag_name, unit = mag_unit)
            mag_table.add_column(e_new_col, index = len(mag_table[0]))
        return mag_table

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    warnings.filterwarnings("ignore")
    # measure times
    start_time = time.time()
    # get property from argv
    fits_name=argv[-1]
    phot = phot_control(fits_name, "aperphot")
    phot.save()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
